use std::{error, fs};
use serde::{Serialize, Deserialize};

use crate::sample;

pub const SAMPLE_RATE: f64 = 44100.0;


#[derive(Serialize, Deserialize, Debug)]
pub struct SequencedSample {
    pub name: String,
    pub sequence: Vec<bool>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Pattern {
    pub length_bars: usize,
    pub sequenced_samples: Vec<SequencedSample>
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Song {
    pub tempo: f64,
    pub length_bars: usize,
    pub patterns: Vec<Pattern>,
    pub arrangement: Vec<Vec<bool>>,
}


impl SequencedSample {
    pub fn write(&self, tempo: f64) -> Result<Vec<(f64, f64)>, Box<dyn error::Error>> {
        let beats_num = self.sequence.len() / 4;
        let beat_length = (SAMPLE_RATE / tempo) as usize;

        let sample = sample::read(&self.name)?;
        let total_length = beat_length * beats_num + sample.len();

        let mut audio: Vec<(f64, f64)> = vec![(0.0, 0.0); total_length];

        for (sequence_i, sample_hits) in (&self.sequence).iter().enumerate() {
            if *sample_hits {
                for k in 0..sample.len() {
                    let i = beat_length/4 * sequence_i + k;
                    if i > total_length { break; }
                    audio[i].0 += sample[k].0;
                    audio[i].1 += sample[k].1;
                }
            }
        }

        Ok(audio)
    }
}


impl Pattern {
    pub fn write(&self, tempo: f64) -> Result<Vec<(f64, f64)>, Box<dyn error::Error>> {
        let beats_num = self.length_bars * 4;
        let beat_length = (SAMPLE_RATE / tempo) as usize;
        let total_length = beat_length * beats_num;

        let mut audio: Vec<(f64, f64)> = vec![(0.0, 0.0); total_length];

        for sequenced_sample in &self.sequenced_samples {
            let written_sample = sequenced_sample.write(tempo)?;

            for i in 0..total_length {
                audio[i].0 += written_sample[i].0;
                audio[i].1 += written_sample[i].1;
            }
        }

        Ok(audio)
    }
}


impl Song {
    pub fn write(&self) -> Result<Vec<(f64, f64)>, Box<dyn error::Error>> {
        let tempo_bps = self.tempo / 60.0;

        let beats_num = self.length_bars * 4;
        let beat_length = (SAMPLE_RATE / tempo_bps) as usize;
        let total_length = beat_length * beats_num;

        let mut audio: Vec<(f64, f64)> = vec![(0.0, 0.0); total_length];

        for (pattern_i, pattern_v) in (&self.patterns).iter().enumerate() {
            let written_pattern = pattern_v.write(tempo_bps)?;

            for (song_i, pattern_hits) in (&self.arrangement)[pattern_i].iter().enumerate() {
                if *pattern_hits {
                    for k in 0..written_pattern.len() {
                        let i = beat_length * 4 * song_i + k;
                        if i > total_length { break; }
                        audio[i].0 += written_pattern[k].0;
                        audio[i].1 += written_pattern[k].1;
                    }
                }
            }
        }

        Ok(audio)
    }

    pub fn serialize(&self, path: &str) -> Result<(), Box<dyn error::Error>> {
        let serialized = serde_json::to_string(self)?;
        fs::write(path, serialized)?;
        Ok(())
    }

    pub fn deserialize(path: &str) -> Result<Song, Box<dyn error::Error>> {
        let json = fs::read_to_string(path)?;
        let deserialized = serde_json::from_str(&json)?;
        Ok(deserialized)
    }
}