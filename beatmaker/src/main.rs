use std::env;
use std::io;
use std::error;

mod song;
mod sample;
mod file;

fn main() -> Result<(), Box<dyn error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        return Err(io::Error::new(io::ErrorKind::Other, "Bad arguments").into());
    }

    let song = song::Song::deserialize(&args[1])?;

    let audio: Vec<(f64, f64)> = song.write()?;
    file::write_wav(&args[2], &audio)?;

    Ok(())
}
