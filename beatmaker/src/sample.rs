use hound;
use std::io;
use std::fs;


fn read_pairs<T, F>(
    reader: &mut hound::WavReader<io::BufReader<fs::File>>,
    normalize: F,
) -> Result<Vec<(f64, f64)>, hound::Error>
where
    T: hound::Sample,
    F: Fn(T) -> f64,
{
    let mut samples = reader.samples::<T>();
    let mut out = Vec::new();

    while let (Some(l), Some(r)) = (samples.next(), samples.next()) {
        out.push((normalize(l?), normalize(r?)));
    }

    Ok(out)
}


pub fn read(filename: &str) -> Result<Vec<(f64, f64)>, hound::Error> {
    let mut reader = hound::WavReader::open(filename)?;
    let spec = reader.spec();

    match (spec.sample_format, spec.bits_per_sample) {
        (hound::SampleFormat::Int, 16) =>
            read_pairs::<i16, _>(&mut reader, |x| x as f64 / i16::MAX as f64),

        (hound::SampleFormat::Int, 24) =>
            read_pairs::<i32, _>(&mut reader, |x| x as f64 / 8_388_608.0),

        (hound::SampleFormat::Int, 32) =>
            read_pairs::<i32, _>(&mut reader, |x| x as f64 / i32::MAX as f64),

        (hound::SampleFormat::Float, 32) =>
            read_pairs::<f32, _>(&mut reader, |x| x as f64),

        _ => panic!("Unsupported WAV format"),
    }
}