use pyo3::prelude::*;

pub mod song;
pub mod sample;
pub mod file;

mod api;

#[pymodule]
fn beatmaker_backend(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = m.py();
    api::file::register(py, m)?;

    Ok(())
}