use hound;
use std::io;
use std::fs;
use std::error;
use crate::beat::SAMPLE_RATE;


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

pub fn write_wav(path: &str, audio: &Vec<(f64, f64)>) -> Result<(), Box<dyn error::Error>> {
    let spec = hound::WavSpec {
        channels: 2,
        sample_rate: SAMPLE_RATE as u32,
        bits_per_sample: 32,
        sample_format: hound::SampleFormat::Int,
    };

    let mut writer = hound::WavWriter::create(path, spec)?;

    for (l, r) in audio {
        writer.write_sample((l.clamp(-1.0, 1.0) * i32::MAX as f64) as i32)?;
        writer.write_sample((r.clamp(-1.0, 1.0) * i32::MAX as f64) as i32)?;
    }

    writer.finalize()?;

    Ok(())
}