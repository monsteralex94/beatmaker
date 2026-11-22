use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;

use pythonize::depythonize;

use crate::song::Song;
use crate::file::write_wav;


#[pyfunction]
pub fn export(song: &Bound<'_, PyAny>, path: &str) -> PyResult<()> {
    let song: Song = depythonize(song)?;
    let audio: Vec<(f64, f64)> = song.write().map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    write_wav(path, &audio).map_err(|e| PyRuntimeError::new_err(e.to_string()))?;

    Ok(())
}


pub fn register(
    py: Python<'_>,
    parent: &Bound<'_, PyModule>,
) -> PyResult<()> {
    let file = PyModule::new(py, "file")?;
    file.add_function(wrap_pyfunction!(export, &file)?)?;
    parent.add_submodule(&file)?;

    py.import("sys")?
        .getattr("modules")?
        .set_item("beatmaker_backend.file", &file)?;

    Ok(())
}
