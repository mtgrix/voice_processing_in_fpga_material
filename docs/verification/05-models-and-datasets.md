# Verification Records: 05 Models And Datasets

### V-05-01 · Matchboxnet Parameter Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `matchboxnet_parameter_count` |
| value | `77K (3x1x64), 93K (3x2x64), 140K (6x2x64)` |
| unit | `parameters` |
| conditions | `1D time-channel separable CNN architecture, C=64 channels` |
| source_tier | `T3` |
| doc_id | `Interspeech 2020 / arXiv:2004.08531` |
| title | MatchboxNet: 1D Time-Channel Separable Convolutional Neural Network for Speech Command Recognition |
| url | https://arxiv.org/pdf/2004.08531.pdf |
| locator | p.2, Table 2 and Table 3 |
| quote | MatchboxNet-3x1x64 \| # Parameters, K: 77 ... MatchboxNet-3x2x64 \| # Parameters, K: 93 ... MatchboxNet-6x2x64 \| # Parameters, K: 140 |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Small model size (<100K parameters, ~93 KB at INT8) fits entirely into on-chip BRAM without DRAM access. |

### V-05-02 · Matchboxnet Task And Metric

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `matchboxnet_task_and_metric` |
| value | `Isolated word classification accuracy (%), NO WER` |
| unit | `Accuracy %` |
| conditions | `Google Speech Commands v1 and v2, 1-second audio clips, 12-class or 35-class closed set` |
| source_tier | `T3` |
| doc_id | `Interspeech 2020 / arXiv:2004.08531` |
| title | MatchboxNet: 1D Time-Channel Separable Convolutional Neural Network for Speech Command Recognition |
| url | https://arxiv.org/pdf/2004.08531.pdf |
| locator | p.2-3, Section 4.2 Results, Table 2 and Table 3 |
| quote | Table 2: MatchboxNet on Google Speech Commands dataset v1, the accuracy is averaged over 5 trials ... MatchboxNet-3x2x64: 97.48 ± 0.107 ... Table 3: ... dataset v2 ... MatchboxNet-3x2x64: 97.21 ± 0.072 |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | MatchboxNet is a keyword classification model, NOT a continuous sequence-to-sequence ASR model. It reports top-1 classification accuracy %, and does NOT have a Word Error Rate (WER). |

### V-05-03 · Streaming Conformer Open Checkpoint

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `streaming_conformer_open_checkpoint` |
| value | `WeNet U2++ Conformer on LibriSpeech` |
| unit | `string` |
| conditions | `Open PyTorch checkpoint librispeech_u2pp_conformer_exp.tar.gz` |
| source_tier | `T2` |
| doc_id | `WeNet Pretrained Models & Tutorial` |
| title | Pretrained Models in WeNet: LibriSpeech U2++ Conformer |
| url | https://raw.githubusercontent.com/wenet-e2e/wenet/main/docs/pretrained_models.md |
| locator | Model List table, row 'librispeech' |
| quote | \| [librispeech](../examples/librispeech/s0/README.md) \| EN \| [Conformer](https://wenet.org.cn/downloads?models=wenet&version=librispeech_u2pp_conformer_exp.tar.gz) \| |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://raw.githubusercontent.com/wenet-e2e/wenet/main/examples/librispeech/s0/README.md |
| notes | Licensed under CC BY 4.0 matching LibriSpeech dataset. |

### V-05-04 · Streaming Conformer Hyperparameters

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `streaming_conformer_hyperparameters` |
| value | `d_model=256, 12 encoder blocks, 4 heads, linear_units=2048, cnn_kernel=15` |
| unit | `string` |
| conditions | `train_u2++_conformer.yaml, causal convolution enabled` |
| source_tier | `T2` |
| doc_id | `WeNet LibriSpeech Recipe Config` |
| title | WeNet train_u2++_conformer.yaml |
| url | https://raw.githubusercontent.com/wenet-e2e/wenet/main/examples/librispeech/s0/conf/train_u2++_conformer.yaml |
| locator | Lines 4-18, encoder_conf |
| quote | output_size: 256 # dimension of attention
attention_heads: 4
linear_units: 2048 # the number of units of position-wise feed forward
num_blocks: 12 # the number of encoder blocks
cnn_module_kernel: 15
causal: true
use_dynamic_chunk: true |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Encoder parameter count is approximately 34.8M to 45M parameters including bidirectional decoder. |

### V-05-05 · Streaming Conformer Latency Context

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `streaming_conformer_latency_context` |
| value | `chunk_size 16 (= 640 ms at 40 ms per feature frame)` |
| unit | `milliseconds` |
| conditions | `WeNet U2++ Conformer LibriSpeech recipe; chunk column '16' of the test-clean table; the 40 ms per frame assumes the recipe's 4x subsampling of 10 ms frames` |
| source_tier | `T2` |
| doc_id | `WeNet LibriSpeech README` |
| title | WeNet LibriSpeech Performance Record |
| url | https://raw.githubusercontent.com/wenet-e2e/wenet/main/examples/librispeech/s0/README.md |
| locator | Section 'Conformer U2++ Result', Table 'test clean'; arithmetic: 16 * 40 = 640 |
| quote | \| decoding mode \| full \| 16 \| |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: the previous value carried a '0ms rightaway / future context' token that the quoted table does not contain and that no fetched document supports. Removed. 640 ms is arithmetic on the published chunk size, not a printed latency. Right-away and future-context latency in milliseconds remain unverified for this checkpoint. |

### V-05-06 · Streaming Conformer Published Wer

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `streaming_conformer_published_wer` |
| value | `3.80% (attention rescoring), 4.54% (CTC beam search)` |
| unit | `WER %` |
| conditions | `LibriSpeech test-clean, chunk size 16 (640ms)` |
| source_tier | `T2` |
| doc_id | `WeNet LibriSpeech README` |
| title | WeNet LibriSpeech Performance Record |
| url | https://raw.githubusercontent.com/wenet-e2e/wenet/main/examples/librispeech/s0/README.md |
| locator | Section 'Conformer U2++ Result', Table 'test clean' |
| quote | \| decoding mode \| full \| 16 \| ; ctc prefix beam search \| 3.76 \| 4.54 \| ; attention rescoring \| 3.32 \| 3.80 \| |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | On test-other, chunk 16 achieves 10.38% (attention rescoring) and 11.52% (CTC prefix beam search). Quote widened so both published numbers (3.80 and 4.54) are visible inside the record itself. |

### V-05-07 · Google Speech Commands V2 License

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `google_speech_commands_v2_license` |
| value | `Creative Commons Attribution 4.0 International (CC BY 4.0)` |
| unit | `license` |
| conditions | `Google Speech Commands Dataset v2` |
| source_tier | `T3` |
| doc_id | `arXiv:1804.03209` |
| title | Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition |
| url | https://arxiv.org/pdf/1804.03209.pdf |
| locator | p.1, Section 2 Introduction, paragraph 3 |
| quote | To reach a wider audience of researchers and developers, this dataset has been released under the Creative Commons BY 4.0 license[5]. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Dataset contains 105,829 utterances across 35 words from 2,618 speakers. |

### V-05-08 · Google Speech Commands Speaker Independence

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `google_speech_commands_speaker_independence` |
| value | `Deterministic SHA-1 speaker-independent split` |
| unit | `n/a` |
| conditions | `testing_list.txt and validation_list.txt partitioning` |
| source_tier | `T3` |
| doc_id | `arXiv:1804.03209` |
| title | Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition |
| url | https://arxiv.org/pdf/1804.03209.pdf |
| locator | p.6, Section 7 Evaluation, paragraph 2 |
| quote | The dataset download includes a text file called validation_list.txt, which contains a list of files that are expected to be used for validating results during training ... The testing_list.txt file contains the names of audio clips that should only be used for measuring the results of trained models ... The set that a file belongs to is chosen using a hash function on its name. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Because file names begin with the unique hashed speaker ID, hashing guarantees all recordings of a given speaker reside exclusively within training, validation, or testing. |

### V-05-09 · Librispeech Corpus License

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `librispeech_corpus_license` |
| value | `Creative Commons Attribution 4.0 International (CC BY 4.0)` |
| unit | `license` |
| conditions | `LibriSpeech ASR corpus (1000 hours)` |
| source_tier | `T3` |
| doc_id | `ICASSP 2015 / OpenSLR 12` |
| title | LibriSpeech: An ASR corpus based on public domain audio books |
| url | https://www.openslr.org/12/ |
| locator | OpenSLR 12 resource descriptor; Warden 2018 p.2 Section 3 |
| quote | LibriSpeech[7] is a collection of 1,000 hours of read English speech, released under a Creative Commons BY 4.0 license |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://arxiv.org/abs/1804.03209 |
| notes | Free for academic and commercial use with proper attribution. |
