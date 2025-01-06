use std::sync::Arc;

use object_store::memory::InMemory;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyString;

/// A Python-facing wrapper around an [`InMemory`].
#[pyclass(name = "MemoryStore", frozen)]
pub struct PyMemoryStore(Arc<InMemory>);

impl AsRef<Arc<InMemory>> for PyMemoryStore {
    fn as_ref(&self) -> &Arc<InMemory> {
        &self.0
    }
}

impl<'py> PyMemoryStore {
    /// Consume self and return the underlying [`InMemory`].
    pub fn into_inner(self) -> Arc<InMemory> {
        self.0
    }

    fn __repr__(&'py self, py: Python<'py>) -> &'py Bound<'py, PyString> {
        intern!(py, "MemoryStore")
    }
}

#[pymethods]
impl PyMemoryStore {
    #[new]
    fn py_new() -> Self {
        Self(Arc::new(InMemory::new()))
    }
}
