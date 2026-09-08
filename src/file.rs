use std::error;
use crate::song::SAMPLE_RATE;

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