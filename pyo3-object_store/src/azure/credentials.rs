use std::sync::Arc;

use async_trait::async_trait;
use chrono::{DateTime, Utc};
use object_store::azure::{AzureAccessKey, AzureCredential};
use object_store::CredentialProvider;
use percent_encoding::percent_decode_str;
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::pybacked::PyBackedStr;

use crate::azure::error::Error;
use crate::credentials::{TemporaryToken, TokenCache};
use crate::PyObjectStoreError;

struct PyAzureAccessKey {
    access_key: AzureAccessKey,
    expires_at: Option<DateTime<Utc>>,
}

// Extract the dict {"access_key": str}
impl<'py> FromPyObject<'py> for PyAzureAccessKey {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let s = ob
            .get_item(intern!(ob.py(), "access_key"))?
            .extract::<PyBackedStr>()?;
        let access_key =
            AzureAccessKey::try_new(&s).map_err(|err| PyValueError::new_err(err.to_string()))?;
        let expires_at = ob.get_item(intern!(ob.py(), "expires_at"))?.extract()?;
        Ok(Self {
            access_key,
            expires_at,
        })
    }
}

struct PyAzureSASToken {
    sas_token: Vec<(String, String)>,
    expires_at: Option<DateTime<Utc>>,
}

// Extract the dict {"sas_token": str | list[tuple[str, str]]}
impl<'py> FromPyObject<'py> for PyAzureSASToken {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let expires_at = ob.get_item(intern!(ob.py(), "expires_at"))?.extract()?;
        let py_sas_token = ob.get_item(intern!(ob.py(), "sas_token"))?;
        if let Ok(sas_token_str) = py_sas_token.extract::<PyBackedStr>() {
            Ok(Self {
                sas_token: split_sas(&sas_token_str).map_err(PyObjectStoreError::from)?,
                expires_at,
            })
        } else if let Ok(sas_token_list) = py_sas_token.extract() {
            Ok(Self {
                sas_token: sas_token_list,
                expires_at,
            })
        } else {
            Err(PyTypeError::new_err(
                "Expected a string or list[tuple[str, str]]",
            ))
        }
    }
}

struct PyBearerToken {
    token: String,
    expires_at: Option<DateTime<Utc>>,
}

// Extract the dict {"token": str}
impl<'py> FromPyObject<'py> for PyBearerToken {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let token = ob.get_item(intern!(ob.py(), "token"))?.extract()?;
        let expires_at = ob.get_item(intern!(ob.py(), "expires_at"))?.extract()?;
        Ok(Self { token, expires_at })
    }
}

#[derive(FromPyObject)]
enum PyAzureCredential {
    AccessKey(PyAzureAccessKey),
    SASToken(PyAzureSASToken),
    BearerToken(PyBearerToken),
}

impl PyAzureCredential {
    fn into_temporary_token(self) -> TemporaryToken<Arc<AzureCredential>> {
        let (credential, expiry) = match self {
            Self::AccessKey(key) => (AzureCredential::AccessKey(key.access_key), key.expires_at),
            Self::SASToken(token) => (AzureCredential::SASToken(token.sas_token), token.expires_at),
            Self::BearerToken(token) => {
                (AzureCredential::BearerToken(token.token), token.expires_at)
            }
        };

        TemporaryToken {
            token: Arc::new(credential),
            expiry,
        }
    }
}

impl From<PyAzureCredential> for AzureCredential {
    fn from(value: PyAzureCredential) -> Self {
        match value {
            PyAzureCredential::AccessKey(key) => Self::AccessKey(key.access_key),
            PyAzureCredential::SASToken(token) => Self::SASToken(token.sas_token),
            PyAzureCredential::BearerToken(token) => Self::BearerToken(token.token),
        }
    }
}

// Vendored from upstream
// https://github.com/apache/arrow-rs/blob/92cfd99e9ab4a6c54500ec65252027b9edf1ee55/object_store/src/azure/builder.rs#L1055-L1072
fn split_sas(sas: &str) -> Result<Vec<(String, String)>, object_store::Error> {
    let sas = percent_decode_str(sas)
        .decode_utf8()
        .map_err(|source| Error::DecodeSasKey { source })?;
    let kv_str_pairs = sas
        .trim_start_matches('?')
        .split('&')
        .filter(|s| !s.chars().all(char::is_whitespace));
    let mut pairs = Vec::new();
    for kv_pair_str in kv_str_pairs {
        let (k, v) = kv_pair_str
            .trim()
            .split_once('=')
            .ok_or(Error::MissingSasComponent {})?;
        pairs.push((k.into(), v.into()))
    }
    Ok(pairs)
}

#[derive(Debug)]
pub struct PyAzureCredentialProvider {
    /// The provided user callback to manage credential refresh
    user_callback: PyObject,
    cache: TokenCache<Arc<AzureCredential>>,
}

impl Clone for PyAzureCredentialProvider {
    fn clone(&self) -> Self {
        let cloned_callback = Python::with_gil(|py| self.user_callback.clone_ref(py));
        Self {
            user_callback: cloned_callback,
            cache: self.cache.clone(),
        }
    }
}

impl<'py> FromPyObject<'py> for PyAzureCredentialProvider {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        if !ob.hasattr(intern!(ob.py(), "__call__"))? {
            return Err(PyTypeError::new_err(
                "Expected callable object for credential_provider.",
            ));
        }

        let mut cache = TokenCache::default();
        if let Ok(refresh_threshold) = ob.getattr(intern!(ob.py(), "refresh_threshold")) {
            cache = cache.with_min_ttl(refresh_threshold.extract()?);
        }
        Ok(Self {
            user_callback: ob.clone().unbind(),
            cache,
        })
    }
}

impl<'py> IntoPyObject<'py> for PyAzureCredentialProvider {
    type Target = PyAny;
    type Output = Bound<'py, PyAny>;
    type Error = PyErr;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Ok(self.user_callback.bind(py).clone())
    }
}

enum PyCredentialProviderResult {
    Async(PyObject),
    Sync(PyAzureCredential),
}

impl PyCredentialProviderResult {
    async fn resolve(self) -> PyResult<PyAzureCredential> {
        match self {
            Self::Sync(credentials) => Ok(credentials),
            Self::Async(coroutine) => {
                let future = Python::with_gil(|py| {
                    pyo3_async_runtimes::tokio::into_future(coroutine.bind(py).clone())
                })?;
                let result = future.await?;
                Python::with_gil(|py| result.extract(py))
            }
        }
    }
}

impl<'py> FromPyObject<'py> for PyCredentialProviderResult {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        if let Ok(credentials) = ob.extract() {
            Ok(Self::Sync(credentials))
        } else {
            Ok(Self::Async(ob.clone().unbind()))
        }
    }
}

impl PyAzureCredentialProvider {
    async fn call(&self) -> PyResult<PyAzureCredential> {
        let call_result = Python::with_gil(|py| {
            self.user_callback
                .call0(py)?
                .extract::<PyCredentialProviderResult>(py)
        })?;
        call_result.resolve().await
    }

    /// Call the user-provided callback
    async fn fetch_token(&self) -> object_store::Result<TemporaryToken<Arc<AzureCredential>>> {
        let credential = self
            .call()
            .await
            .map_err(|err| object_store::Error::Generic {
                store: "External Azure credential provider",
                source: Box::new(err),
            })?;

        Ok(credential.into_temporary_token())
    }
}

// TODO: store expiration time and only call the external Python function as needed
#[async_trait]
impl CredentialProvider for PyAzureCredentialProvider {
    type Credential = AzureCredential;

    async fn get_credential(&self) -> object_store::Result<Arc<Self::Credential>> {
        self.cache.get_or_insert_with(|| self.fetch_token()).await
    }
}
