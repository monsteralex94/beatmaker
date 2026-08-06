use std::fs;
use std::env;
use std::io;
use std::error;

mod beat;
mod sample;

fn main() -> Result<(), Box<dyn error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        return Err(io::Error::new(io::ErrorKind::Other, "Bad arguments").into());
    }

    let contents = fs::read_to_string(&args[1])?;
    let lines: Vec<&str> = contents.lines().collect();

    let mut sequence: Vec<Vec<bool>> = vec![vec![false; lines[0].len()]; lines.len()];
    beat::read_sequence(&lines, &mut sequence);

    let audio: Vec<(f64, f64)> = beat::write_sequence(&sequence)?;
    sample::write_wav(&args[2], &audio)?;

    Ok(())
}
