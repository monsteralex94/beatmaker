use crate::sample;

pub const SAMPLE_RATE: f64 = 44100.0;
pub const TEMPO: f64 = 140.0 / 60.0;

pub fn read_sequence(lines: &Vec<&str>, sequence: &mut Vec<Vec<bool>>) -> () {
    for (i, line) in lines.iter().enumerate() {
        for (j, char) in line.chars().enumerate() {
            sequence[i][j] = char != '.';
        }
    }
}

pub fn write_sequence(sequence: &Vec<Vec<bool>>) -> Result<Vec<(f64, f64)>, Box<dyn std::error::Error>> {
    let beats_num = sequence[0].len() / 4;
    let beat_length = (SAMPLE_RATE / TEMPO) as usize;
    //let total_length = beat_length * beats_num;

    let samples: Vec<Vec<(f64, f64)>> = vec![
        sample::read("samples/kick.wav")?,
        sample::read("samples/snare.wav")?,
        sample::read("samples/hihat.wav")?,
    ];

    let longest_sample = samples.iter().map(Vec::len).max().unwrap();
    let total_length = beat_length * beats_num + longest_sample;

    let mut audio: Vec<(f64, f64)> = vec![(0.0, 0.0); total_length];

    for (row_i, row_v) in sequence.iter().enumerate() {
        for time_i in 0..row_v.len() {
            if row_v[time_i] {
                let sample = &samples[row_i];

                for k in 0..sample.len() {
                    let i = beat_length/4 * time_i + k;

                    if i >= total_length {
                        break;
                    }

                    audio[i].0 += sample[k].0;
                    audio[i].1 += sample[k].1;
                }
            }
        }
    }

    Ok(audio)
}