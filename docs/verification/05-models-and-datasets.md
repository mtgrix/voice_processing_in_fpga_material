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
| doc_id | `arXiv:1804.03209` |
| title | Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition |
| url | https://arxiv.org/pdf/1804.03209.pdf |
| locator | p.2, section 3, sentence introducing the LibriSpeech corpus (its reference [7]) |
| quote | LibriSpeech[7] is a collection of 1,000 hours of read English speech, released under a Creative Commons BY 4.0 license |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://www.openslr.org/12/ |
| notes | Registered 2026-09-13 against the document the quote was actually read from. The value is Warden's characterisation of a third party's corpus, not the corpus's own licence page, so the tier describes the citing paper (T3) and the sentence remains secondary evidence about LibriSpeech. The authoritative statement is the OpenSLR 12 page, held by V-05-10 as T4; that page was fetched the same day for its sample-rate sentence and was not re-read for licence wording, so no quote is claimed from it here. Panayotov et al., ICASSP 2015 -- the primary description -- is still unretrieved: the IEEE page is paywalled and no arXiv copy exists, recorded in V-05-10's notes as well. Previously this record carried doc_id 'ICASSP 2015 / OpenSLR 12', a title naming the ICASSP paper, a url naming the corpus page and a quote from Warden: three fields, three documents. |

### V-05-10 · Librispeech Audio Sample Rate

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `librispeech_audio_sample_rate` |
| value | `16` |
| unit | `kHz` |
| conditions | `LibriSpeech ASR corpus, complete set, read English speech from audiobooks` |
| source_tier | `T4` |
| doc_id | `OpenSLR 12` |
| title | LibriSpeech ASR corpus |
| url | https://www.openslr.org/12/ |
| locator | Openslr.org/12 resource page, corpus description, first sentence |
| quote | LibriSpeech is a corpus of approximately 1000 hours of 16kHz read English speech, prepared by Vassil Panayotov with the assistance of Daniel Povey. |
| retrieved_utc | `2026-09-13T10:43:23Z` |
| access | `open` |
| corroborating_url |  |
| notes | The number is the corpus's own storage rate as stated by its distribution page, not the input rate of any model. Tier T4 is admissible as corroboration only under docs/WEB_SEARCH_PROTOCOL.md section 2, so this record does not stand alone: the peer-reviewed description (Panayotov et al., ICASSP 2015) would upgrade it and was not reachable in this pass -- the IEEE page is paywalled and no arXiv copy exists. V-05-11 carries the same quantity from a T3 source for the other corpus the benchmark set uses, and the book's frontend parameter rests on that pair, not on this row alone. doc_id renamed from 'ICASSP 2015 / OpenSLR 12' on 2026-09-13: this record reads only the corpus page, and the conference name in the old id belonged to a different work -- see V-05-09, which now carries the Warden sentence it quoted. |

### V-05-11 · Speech Commands Audio Sample Rate

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `speech_commands_audio_sample_rate` |
| value | `16` |
| unit | `kHz` |
| conditions | `Google Speech Commands dataset, 105,829 utterances of 35 words, one second or less each` |
| source_tier | `T3` |
| doc_id | `arXiv:1804.03209` |
| title | Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition |
| url | https://arxiv.org/pdf/1804.03209.pdf |
| locator | p.6, section 6 Properties |
| quote | Each utterance is stored as a one-second (or less) WAVE format file, with the sample data encoded as linear 16-bit single-channel PCM values, at a 16 KHz rate. |
| retrieved_utc | `2026-09-13T10:43:23Z` |
| access | `open` |
| corroborating_url |  |
| notes | Read from the same arXiv PDF that V-05-07 and V-05-08 cite; the copy examined carries the page-1 stamp arXiv:1804.03209v1 [cs.CL] 9 Apr 2018, and the revision is recorded here rather than in doc_id, because one document gets one identifier and a v1 suffix would have counted this paper as a second source. The publication venue was not verified from the fetched document. The TensorFlow Datasets catalogue page for speech_commands was fetched on the same pass and does NOT state a sample rate -- it lists audio as int16 with an unbounded shape -- so the paper is the source and the catalogue is not cited for this. Same rate as V-05-10, which is why the frontend of chapter 1 can use 16,000 Hz for both models in the benchmark set. |

### V-05-12 · Nemo Conformer Small Encoder Layers

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_small_encoder_layers` |
| value | `16` |
| unit | `encoder blocks` |
| conditions | `Conformer-Transducer, Small variant, as NVIDIA's recipe prints it; the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 11, the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it; column 'n_layers' |
| quote | #  \| Small   (14M)\|   176   \|    4   \|    16     \|       31         \|     0.0      \|           320            \|        1        \| |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | The report claim that the book's model has 16 blocks is right for the NeMo reading of the spine, and was answered here with the repository holding no NeMo record at all. The WeNet reading registered in V-05-04 says 12 for the same field, and C-08 records the split. |

### V-05-13 · Nemo Conformer Small D Model

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_small_d_model` |
| value | `176` |
| unit | `hidden units` |
| conditions | `Conformer-Transducer, Small variant; the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 11, the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it; column 'd_model' |
| quote | #  \| Small   (14M)\|   176   \|    4   \|    16     \|       31         \|     0.0      \|           320            \|        1        \| |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | The width every buffer and MAC count in chapter 9 is built from. The WeNet reading registers 256 for the same field. |

### V-05-14 · Nemo Conformer Small Attention Heads

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_small_attention_heads` |
| value | `4` |
| unit | `attention heads` |
| conditions | `Conformer-Transducer, Small variant; the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 11, the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it; column 'n_heads' |
| quote | #  \| Small   (14M)\|   176   \|    4   \|    16     \|       31         \|     0.0      \|           320            \|        1        \| |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | Four heads across 176 units gives d_head 44, which is not a power of two, so a fixed-point head index cannot be formed by a shift for this variant even though it can for the Large one in V-05-19. Arithmetic: 176 / 4 = 44. |

### V-05-15 · Nemo Conformer Small Conv Kernel Size

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_small_conv_kernel_size` |
| value | `31` |
| unit | `convolution taps` |
| conditions | `Conformer-Transducer, Small variant; the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 11, the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it; column 'conv_kernel_size' |
| quote | #  \| Small   (14M)\|   176   \|    4   \|    16     \|       31         \|     0.0      \|           320            \|        1        \| |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | Depthwise taps in the convolution module. The WeNet reading registers 15 for the same field. Every variant in that table but XLarge keeps 31, so this is a fixed property of the family rather than a size knob. |

### V-05-16 · Nemo Conformer Small Parameter Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_small_parameter_count` |
| value | `about 14 million` |
| unit | `parameters` |
| conditions | `Whole model, encoder plus Transducer decoder, as the recipe rounds it; the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 11, the recommended-variants table in the config header, whose column names are printed at line 9 in the order d_model, n_heads, n_layers, conv_kernel_size, weight_decay, pred_hidden/joint_hidden, pred_rnn_layers; the preamble at line 6 says of that table that "other parameters are the same as in this config file", so a Small model is this row read against the body below it; the model column reads 'Small   (14M)' |
| quote | #  \| Small   (14M)\|   176   \|    4   \|    16     \|       31         \|     0.0      \|           320            \|        1        \| |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | An approximation the publisher prints about its own recipe, not a counted figure. No record carries an encoder-only count, and the checkpoint manifest that would give one is gated: an anonymous request for the HuggingFace repository of this model answered HTTP 401. |

### V-05-17 · Nemo Conformer Offline Large Encoder Layers

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_offline_large_encoder_layers` |
| value | `17` |
| unit | `encoder blocks` |
| conditions | `the config body of offline Conformer-Transducer recipe config `conformer/conformer_transducer_bpe.yaml`, which holds the Large defaults that line 1 rounds to ~120M` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 122, model.encoder.n_layers |
| quote |     n_layers: 17 |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | Seventeen against the Small variant's 16 at V-05-12, so the two readings of the block count differ by one because they describe two different models, not because either is wrong. |

### V-05-18 · Nemo Conformer Offline Large D Model

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_offline_large_d_model` |
| value | `512` |
| unit | `hidden units` |
| conditions | `the config body of offline Conformer-Transducer recipe config `conformer/conformer_transducer_bpe.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 123, model.encoder.d_model |
| quote |     d_model: 512 |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-05-19 · Nemo Conformer Offline Large Attention Heads

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_offline_large_attention_heads` |
| value | `8` |
| unit | `attention heads` |
| conditions | `the config body of offline Conformer-Transducer recipe config `conformer/conformer_transducer_bpe.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 143, model.encoder.n_heads |
| quote |     n_heads: 8 # may need to be lower for smaller d_models |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | Five hundred twelve over eight gives d_head 64, a power of two, so at the Large default width a head index is a shift and a head slice is a byte range. Arithmetic: 512 / 8 = 64. |

### V-05-20 · Nemo Conformer Offline Large Conv Norm Type

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_offline_large_conv_norm_type` |
| value | `batch_norm` |
| unit | `string` |
| conditions | `the config body of offline Conformer-Transducer recipe config `conformer/conformer_transducer_bpe.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 153, model.encoder.conv_norm_type, whose trailing comment lists the alternatives 'batch_norm or layer_norm or groupnormN' |
| quote |     conv_norm_type: 'batch_norm' # batch_norm or layer_norm or groupnormN (N specifies the number of groups) |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | The only one of the three recipe configs on record that names BatchNorm, and it is the offline one. Both streaming configs record layer_norm, at V-05-26 and V-05-41. That is the difference the gap-report audit turns on: a BatchNorm folds backwards into the causal depthwise taps as a per-channel affine and deletes a stage, while a LayerNorm is data-dependent, folds into nothing, and must be built as itself. |

### V-05-21 · Nemo Conformer Offline Large Attention Model

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_offline_large_attention_model` |
| value | `rel_pos` |
| unit | `string` |
| conditions | `the config body of offline Conformer-Transducer recipe config `conformer/conformer_transducer_bpe.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/conformer_transducer_bpe.yaml |
| locator | Line 142, model.encoder.self_attention_model, whose trailing comment reads 'rel_pos or abs_pos' |
| quote |     self_attention_model: rel_pos # rel_pos or abs_pos |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | Relative-position attention, the Transformer-XL scheme, confirmed in a second NeMo config after V-05-04's WeNet config said the same in its lines 17 and 18. |

### V-05-22 · Nemo Streaming Conformer Large Encoder Layers

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_large_encoder_layers` |
| value | `17` |
| unit | `encoder blocks` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`, which the header at line 1 rounds to ~120M` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 89, model.encoder.n_layers |
| quote |     n_layers: 17 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | Every block keeps its own key and value cache, so the left-context buffer of plan-v2 section 6.7 is this many times one block's, a multiplier the printed formula omits -- issue #48. |

### V-05-23 · Nemo Streaming Conformer Large D Model

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_large_d_model` |
| value | `512` |
| unit | `hidden units` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 90, model.encoder.d_model |
| quote |     d_model: 512 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-05-24 · Nemo Streaming Conformer Large Attention Heads

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_large_attention_heads` |
| value | `8` |
| unit | `attention heads` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 111, model.encoder.n_heads |
| quote |     n_heads: 8 # may need to be lower for smaller d_models |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | Arithmetic: 512 / 8 = 64. |

### V-05-25 · Nemo Streaming Conformer Large Conv Kernel Size

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_large_conv_kernel_size` |
| value | `31` |
| unit | `convolution taps` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 132, model.encoder.conv_kernel_size, with conv_context_size set to causal at line 138; line 136 of the same file states that 'causal' means [(kernel_size-1), 0] of that pair |
| quote |     conv_kernel_size: 31 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | Thirty-one taps laid out causally is a tap history of 30 encoder steps, so the convolution module alone pushes a frame's support 1.2 s behind the frame itself, before attention is counted. Arithmetic: 31 - 1 = 30; 30 * 4 * 0.01 * 1000 = 1200. |

### V-05-26 · Nemo Streaming Conformer Large Conv Norm Type

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_large_conv_norm_type` |
| value | `layer_norm` |
| unit | `string` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 133, model.encoder.conv_norm_type |
| quote |     conv_norm_type: 'layer_norm' # batch_norm or layer_norm or groupnormN (N specifies the number of groups) |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | The streaming model the spine names normalises its convolution module with LayerNorm, so the unit stays in the chapter's hardware list: a mean, a variance, and a reciprocal square root per frame, computed at runtime, folding into no neighbouring convolution. |

### V-05-27 · Nemo Streaming Conformer Large Attention Model

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_large_attention_model` |
| value | `rel_pos` |
| unit | `string` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 110, model.encoder.self_attention_model |
| quote |     self_attention_model: rel_pos # rel_pos or abs_pos |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | Relative position in the streaming model as well, so the shift term is not something chunking removes; line 128 of the same file unties the biases of what it calls the TransformerXL layers, which names the family outright. |

### V-05-28 · Nemo Streaming Conformer Large Attention Context Style

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_large_attention_context_style` |
| value | `chunked_limited` |
| unit | `string` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 124, model.encoder.att_context_style, whose trailing comment reads 'regular or chunked_limited' |
| quote |     att_context_style: chunked_limited # regular or chunked_limited |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | In this mode a frame attends in both directions inside its own chunk and to a bounded number of earlier chunks. It is the record that settles the strict-causal-mask question for the NeMo reading the way V-05-06's use_dynamic_chunk did for the WeNet one: a frame-level causal mask would delete the right context this line exists to configure. |

### V-05-29 · Nemo Streaming Conformer Left Context

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_left_context` |
| value | `140` |
| unit | `attention steps` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`; an attention step is an encoder frame after subsampling, so 40 ms at the factor 4 and stride 0.01 s registered beside this record` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 123, model.encoder.att_context_size, first element of the pair; line 113 is the file's own comment on what the two elements mean |
| quote |     att_context_size: [140, 27] # -1 means unlimited context |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | The symbol plan-v2 section 6.7 writes as T_left, and the quantity the external report used without ever giving it a value. One hundred forty steps at 40 ms is 5.6 s of left context, which no ring buffer in fabric holds, so the number of chunks actually kept is a design decision the book has to make rather than read off. Arithmetic: 140 * 4 * 0.01 * 1000 = 5600. |

### V-05-30 · Nemo Streaming Conformer Right Context

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_right_context` |
| value | `27` |
| unit | `attention steps` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 123, model.encoder.att_context_size, second element of the pair; line 113 is the file's own comment on what the two elements mean |
| quote |     att_context_size: [140, 27] # -1 means unlimited context |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | The right context the book plots on its latency axis, and the number the report's strict causal mask would set to zero. Line 115 states that in chunked_limited the left context must be divisible by the right context plus one, and 140 / (27 + 1) = 5 exactly; that is an arithmetic observation about the published pair, not a claim about how many chunks the implementation caches. |

### V-05-31 · Nemo Streaming Conformer Feature Window Stride

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_feature_window_stride` |
| value | `0.01` |
| unit | `seconds` |
| conditions | `the mel front end of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`, with window_size 0.025 at line 69, features 80 at line 72 and n_fft 512 at line 73` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 70, model.preprocessor.window_stride |
| quote |     window_stride: 0.01 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | Ten milliseconds per audio frame before subsampling, the unit every frame time in the book converts from. The sample rate on line 67 is not a literal but the reference `${model.sample_rate}`, so it is not registered from this line. |

### V-05-32 · Nemo Streaming Conformer Subsampling Factor

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_subsampling_factor` |
| value | `4` |
| unit | `multiplier` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 95, model.encoder.subsampling_factor, with subsampling set to striding at line 94 and causal_downsampling true at line 97 |
| quote |     subsampling_factor: 4 # must be power of 2 for striding and vggnet |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | Four to one is what turns one attention step into 40 ms of audio. The line's own comment requires the factor to be a power of two for the striding and vggnet frontends, which is a constraint on any fixed-point replacement as well. |

### V-05-33 · Nemo Streaming Conformer Large Parameter Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_large_parameter_count` |
| value | `about 120 million` |
| unit | `parameters` |
| conditions | `the whole model as the recipe rounds it, encoder plus Transducer decoder` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 1, the file's opening description |
| quote | # It contains the default values for training a streaming cache-aware Conformer-Transducer ASR model, large size (~120M) with Transducer loss and sub-word encoding. |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | A rounded figure the publisher prints about its own recipe, not a counted parameter list. |

### V-05-34 · Nemo Streaming Conformer Attention Lookahead

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_attention_lookahead` |
| value | `1080` |
| unit | `milliseconds` |
| conditions | `the cache-aware streaming Conformer-Transducer at its published context size [140, 27]` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 116 prints the formula and a worked example; its three inputs are lines 123, 95 and 70 of the same file, registered as V-05-30, V-05-32 and V-05-31; arithmetic: 27 * 4 * 0.01 * 1000 = 1080 |
| quote |     # look-ahead(secs) = att_context_size[1]*subsampling_factor*window_stride, example: 13*8*0.01=1.04s |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | Derived by the config's own printed formula, whose worked example on the same line is 13*8*0.01=1.04s. A frame cannot be decoded until 1.08 s of later audio has arrived, so this is the algorithmic floor on the model's latency and the reason a strict frame-level causal mask would not describe this checkpoint at all. |

### V-05-35 · Nemo Streaming Conformer Frontend Mel Bands

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_frontend_mel_bands` |
| value | `80` |
| unit | `mel bands` |
| conditions | `the mel front end of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`, feeding model.encoder.feat_in` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 72, model.preprocessor.features |
| quote |     features: 80 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | The encoder's input width, which the book's front-end budget needs and which the WeNet reading has never carried as a record at all. |

### V-05-36 · Nemo Streaming Conformer Ffn Expansion Factor

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_ffn_expansion_factor` |
| value | `4` |
| unit | `multiplier` |
| conditions | `the config body of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 107, model.encoder.ff_expansion_factor |
| quote |     ff_expansion_factor: 4 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | The feed-forward width as a multiple of d_model rather than an absolute, so 512 * 4 = 2048 hidden units per block, which is where most of an encoder block's weights live. Arithmetic: 512 * 4 = 2048. |

### V-05-37 · Nemo Streaming Fastconformer Large Encoder Layers

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_large_encoder_layers` |
| value | `17` |
| unit | `encoder blocks` |
| conditions | `the config body of cache-aware streaming FastConformer-Transducer recipe config `fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml`, which the header at line 1 rounds to ~115M` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 86, model.encoder.n_layers |
| quote |     n_layers: 17 |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-05-38 · Nemo Streaming Fastconformer Large D Model

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_large_d_model` |
| value | `512` |
| unit | `hidden units` |
| conditions | `the config body of cache-aware streaming FastConformer-Transducer recipe config `fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 87, model.encoder.d_model |
| quote |     d_model: 512 |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-05-39 · Nemo Streaming Fastconformer Large Attention Heads

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_large_attention_heads` |
| value | `8` |
| unit | `attention heads` |
| conditions | `the config body of cache-aware streaming FastConformer-Transducer recipe config `fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 101, model.encoder.n_heads |
| quote |     n_heads: 8 # may need to be lower for smaller d_models |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | Arithmetic: 512 / 8 = 64. |

### V-05-40 · Nemo Streaming Fastconformer Large Conv Kernel Size

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_large_conv_kernel_size` |
| value | `9` |
| unit | `convolution taps` |
| conditions | `the config body of cache-aware streaming FastConformer-Transducer recipe config `fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 122, model.encoder.conv_kernel_size, with conv_context_size causal at line 128 |
| quote |     conv_kernel_size: 9 |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | Nine taps where the Conformer uses thirty-one. That is the FastConformer's main structural departure, and in fabric it is a tap history of 8 steps rather than 30, a saving in the convolution module's own state rather than in the attention cache. Arithmetic: 9 - 1 = 8. |

### V-05-41 · Nemo Streaming Fastconformer Large Conv Norm Type

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_large_conv_norm_type` |
| value | `layer_norm` |
| unit | `string` |
| conditions | `the config body of cache-aware streaming FastConformer-Transducer recipe config `fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 123, model.encoder.conv_norm_type |
| quote |     conv_norm_type: 'layer_norm' # batch_norm or layer_norm or groupnormN (N specifies the number of groups) |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | A second streaming config recording LayerNorm, so LayerNorm in the convolution module is the streaming normalisation of this model family and not an artefact of one file. |

### V-05-42 · Nemo Streaming Fastconformer Subsampling Factor

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_subsampling_factor` |
| value | `8` |
| unit | `multiplier` |
| conditions | `the config body of cache-aware streaming FastConformer-Transducer recipe config `fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 92, model.encoder.subsampling_factor, with ff_expansion_factor 4 at line 97 |
| quote |     subsampling_factor: 8 # must be power of 2 for striding and vggnet |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | Eight to one where the Conformer uses four, so one FastConformer encoder step is 80 ms of audio and a chunk of the same step count covers twice the time at half the frames. |

### V-05-43 · Nemo Streaming Fastconformer Left Context

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_left_context` |
| value | `70` |
| unit | `attention steps` |
| conditions | `the config body of cache-aware streaming FastConformer-Transducer recipe config `fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml`; an attention step is 80 ms at the stride and factor registered beside this record` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 113, model.encoder.att_context_size, first element of the pair; line 103 is the file's own comment on what the two elements mean |
| quote |     att_context_size: [70, 13] # -1 means unlimited context |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | Seventy steps at 80 ms is 5.6 s, the same span as the Conformer's 140 steps at 40 ms in V-05-29, reached with half the cache. Arithmetic: 70 * 8 * 0.01 * 1000 = 5600. |

### V-05-44 · Nemo Streaming Fastconformer Right Context

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_right_context` |
| value | `13` |
| unit | `attention steps` |
| conditions | `the config body of cache-aware streaming FastConformer-Transducer recipe config `fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml`` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 113, model.encoder.att_context_size, second element of the pair |
| quote |     att_context_size: [70, 13] # -1 means unlimited context |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | The first entry of the four-entry list the comment at line 111 gives for a multi-lookahead model, [[70,13],[70,6],[70,1],[70,0]], and line 109 states that during test and inference the first item of such a list is the default. That list is the family the score table publishes as separate checkpoints, V-05-52 to V-05-55. |

### V-05-45 · Nemo Streaming Fastconformer Feature Window Stride

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_feature_window_stride` |
| value | `0.01` |
| unit | `seconds` |
| conditions | `the mel front end of cache-aware streaming FastConformer-Transducer recipe config `fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml`, with window_size 0.025 at line 66 and n_fft 512 at line 70` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 67, model.preprocessor.window_stride |
| quote |     window_stride: 0.01 |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-05-46 · Nemo Streaming Fastconformer Large Parameter Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_large_parameter_count` |
| value | `about 115 million` |
| unit | `parameters` |
| conditions | `the whole model as the recipe rounds it` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 1, the file's opening description |
| quote | # It contains the default values for training a cache-aware streaming FastConformer-Transducer ASR model, large size (~115M) with sub-word encoding. |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-05-47 · Nemo Streaming Fastconformer Attention Lookahead

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_attention_lookahead` |
| value | `1040` |
| unit | `milliseconds` |
| conditions | `the cache-aware streaming FastConformer-Transducer at its published context size [70, 13]` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config` |
| title | NeMo fastconformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/25445927d77f0cf5ef897826fc99c22d9b2308ee/examples/asr/conf/fastconformer/cache_aware_streaming/fastconformer_transducer_bpe_streaming.yaml |
| locator | Line 106 prints the formula and a worked example; its three inputs are lines 113, 92 and 67 of the same file, registered as V-05-44, V-05-42 and V-05-45; arithmetic: 13 * 8 * 0.01 * 1000 = 1040 |
| quote |     # look-ahead(secs) = att_context_size[1]*subsampling_factor*window_stride, example: 13*8*0.01=1.04s |
| retrieved_utc | `2026-09-13T21:32:57Z` |
| access | `open` |
| corroborating_url |  |
| notes | NVIDIA's own score table names a checkpoint for this operating point, stt_en_fastconformer_hybrid_large_streaming_1040ms, registered as V-05-48 and V-05-49, so the config's formula and the published catalogue agree without either being derived from the other. |

### V-05-48 · Nemo Streaming Fastconformer 1040Ms Test Clean Wer

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_1040ms_test_clean_wer` |
| value | `2.3` |
| unit | `WER %` |
| conditions | `LibriSpeech test-clean, RNNT decoding of the hybrid checkpoint at its 1040 ms look-ahead` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer English Score Table` |
| title | NeMo docs/source/asr/data/scores/en/conformer_en.csv |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/6f20e61e4d11ce4dafc0f037c3bad535e1ac3ea9/docs/source/asr/data/scores/en/conformer_en.csv |
| locator | Line 20, column 'Librispeech Test-Clean' of the header at line 1, model stt_en_fastconformer_hybrid_large_streaming_1040ms (RNNT) |
| quote | stt_en_fastconformer_hybrid_large_streaming_1040ms (RNNT),en,,,,,2.3 %,5.5 %,,,8.0 %,6.6 %,,,,,,,2.9 %,1.6 % |
| retrieved_utc | `2026-09-13T21:32:58Z` |
| access | `open` |
| corroborating_url |  |
| notes | The accuracy of the streaming model the book can actually obtain, at the operating point V-05-47 derives from a config file. |

### V-05-49 · Nemo Streaming Fastconformer 1040Ms Test Other Wer

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_1040ms_test_other_wer` |
| value | `5.5` |
| unit | `WER %` |
| conditions | `LibriSpeech test-other, RNNT decoding of the hybrid checkpoint at its 1040 ms look-ahead` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer English Score Table` |
| title | NeMo docs/source/asr/data/scores/en/conformer_en.csv |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/6f20e61e4d11ce4dafc0f037c3bad535e1ac3ea9/docs/source/asr/data/scores/en/conformer_en.csv |
| locator | Line 20, column 'Librispeech Test-Other' of the header at line 1, model stt_en_fastconformer_hybrid_large_streaming_1040ms (RNNT) |
| quote | stt_en_fastconformer_hybrid_large_streaming_1040ms (RNNT),en,,,,,2.3 %,5.5 %,,,8.0 %,6.6 %,,,,,,,2.9 %,1.6 % |
| retrieved_utc | `2026-09-13T21:32:58Z` |
| access | `open` |
| corroborating_url |  |
| notes | The printed cell is '5.5 %', with a space before the sign. No streaming Conformer-Transducer row exists in this table at all, which is what V-05-56 records. |

### V-05-50 · Nemo Conformer Offline Small Test Clean Wer

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_offline_small_test_clean_wer` |
| value | `2.5` |
| unit | `WER %` |
| conditions | `LibriSpeech test-clean, offline Conformer-Transducer in the Small variant` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer English Score Table` |
| title | NeMo docs/source/asr/data/scores/en/conformer_en.csv |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/6f20e61e4d11ce4dafc0f037c3bad535e1ac3ea9/docs/source/asr/data/scores/en/conformer_en.csv |
| locator | Line 9, column 'Librispeech Test-Clean' of the header at line 1, model stt_en_conformer_transducer_small |
| quote | stt_en_conformer_transducer_small,en,,,2.8,6.6,2.5,6.6,,,,,,,,,,,, |
| retrieved_utc | `2026-09-13T21:32:58Z` |
| access | `open` |
| corroborating_url |  |
| notes | The small model's accuracy is published only for the offline variant, so 'small' and 'streaming' are two different claims about one device and the spine's phrase joins them. |

### V-05-51 · Nemo Conformer Offline Small Test Other Wer

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_conformer_offline_small_test_other_wer` |
| value | `6.6` |
| unit | `WER %` |
| conditions | `LibriSpeech test-other, offline Conformer-Transducer in the Small variant` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer English Score Table` |
| title | NeMo docs/source/asr/data/scores/en/conformer_en.csv |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/6f20e61e4d11ce4dafc0f037c3bad535e1ac3ea9/docs/source/asr/data/scores/en/conformer_en.csv |
| locator | Line 9, column 'Librispeech Test-Other' of the header at line 1, model stt_en_conformer_transducer_small |
| quote | stt_en_conformer_transducer_small,en,,,2.8,6.6,2.5,6.6,,,,,,,,,,,, |
| retrieved_utc | `2026-09-13T21:32:58Z` |
| access | `open` |
| corroborating_url |  |
| notes | The same figure appears twice on the line: the dev-other and test-other columns both read 6.6, so naming the column in the locator is what decides which one this record states. |

### V-05-52 · Nemo Streaming Fastconformer Multi 0Ms Test Other Wer

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_multi_0ms_test_other_wer` |
| value | `7.0` |
| unit | `WER %` |
| conditions | `LibriSpeech test-other, RNNT decoding, zero look-ahead, from the multi-lookahead family` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer English Score Table` |
| title | NeMo docs/source/asr/data/scores/en/conformer_en.csv |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/6f20e61e4d11ce4dafc0f037c3bad535e1ac3ea9/docs/source/asr/data/scores/en/conformer_en.csv |
| locator | Line 21, column 'Librispeech Test-Other' of the header at line 1, model stt_en_fastconformer_hybrid_large_streaming_multi (RNNT - 0ms) |
| quote | stt_en_fastconformer_hybrid_large_streaming_multi (RNNT - 0ms),en,,,,,,7.0 %,,,,,,,,,,,, |
| retrieved_utc | `2026-09-13T21:32:58Z` |
| access | `open` |
| corroborating_url |  |
| notes | One of four points on the only accuracy-against-latency curve a publisher has drawn for this family; the other three are V-05-53, V-05-54 and V-05-55. Of these four rows only the test-other column is filled, so the curve is one column deep. |

### V-05-53 · Nemo Streaming Fastconformer Multi 80Ms Test Other Wer

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_multi_80ms_test_other_wer` |
| value | `6.4` |
| unit | `WER %` |
| conditions | `LibriSpeech test-other, RNNT decoding, 80 ms look-ahead` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer English Score Table` |
| title | NeMo docs/source/asr/data/scores/en/conformer_en.csv |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/6f20e61e4d11ce4dafc0f037c3bad535e1ac3ea9/docs/source/asr/data/scores/en/conformer_en.csv |
| locator | Line 22, column 'Librispeech Test-Other' of the header at line 1, model stt_en_fastconformer_hybrid_large_streaming_multi (RNNT - 80ms) |
| quote | stt_en_fastconformer_hybrid_large_streaming_multi (RNNT - 80ms),en,,,,,,6.4 %,,,,,,,,,,,, |
| retrieved_utc | `2026-09-13T21:32:58Z` |
| access | `open` |
| corroborating_url |  |
| notes | Eighty milliseconds is one encoder step at the stride and factor registered at V-05-45 and V-05-42, which is also the span of the separately named 80 ms hybrid checkpoint on line 18. |

### V-05-54 · Nemo Streaming Fastconformer Multi 480Ms Test Other Wer

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_multi_480ms_test_other_wer` |
| value | `5.7` |
| unit | `WER %` |
| conditions | `LibriSpeech test-other, RNNT decoding, 480 ms look-ahead; the row label omits the 'ms' suffix that the two rows above it carry` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer English Score Table` |
| title | NeMo docs/source/asr/data/scores/en/conformer_en.csv |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/6f20e61e4d11ce4dafc0f037c3bad535e1ac3ea9/docs/source/asr/data/scores/en/conformer_en.csv |
| locator | Line 23, column 'Librispeech Test-Other' of the header at line 1, model stt_en_fastconformer_hybrid_large_streaming_multi (RNNT - 480) |
| quote | stt_en_fastconformer_hybrid_large_streaming_multi (RNNT - 480),en,,,,,,5.7 %,,,,,,,,,,,, |
| retrieved_utc | `2026-09-13T21:32:58Z` |
| access | `open` |
| corroborating_url |  |
| notes | 480 divided by the 80 ms step is 6, and the multi-lookahead list at line 111 of the config has right contexts of 13, 6, 1 and 0 steps, so this row is the second entry of that list. Arithmetic: 480 / 80 = 6. |

### V-05-55 · Nemo Streaming Fastconformer Multi 1040Ms Test Other Wer

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_fastconformer_multi_1040ms_test_other_wer` |
| value | `5.4` |
| unit | `WER %` |
| conditions | `LibriSpeech test-other, RNNT decoding, 1040 ms look-ahead` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer English Score Table` |
| title | NeMo docs/source/asr/data/scores/en/conformer_en.csv |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/6f20e61e4d11ce4dafc0f037c3bad535e1ac3ea9/docs/source/asr/data/scores/en/conformer_en.csv |
| locator | Line 24, column 'Librispeech Test-Other' of the header at line 1, model stt_en_fastconformer_hybrid_large_streaming_multi (RNNT - 1040) |
| quote | stt_en_fastconformer_hybrid_large_streaming_multi (RNNT - 1040),en,,,,,,5.4 %,,,,,,,,,,,, |
| retrieved_utc | `2026-09-13T21:32:58Z` |
| access | `open` |
| corroborating_url |  |
| notes | The four points are 7.0, 6.4, 5.7 and 5.4 per cent at 0, 80, 480 and 1040 ms. That is the shape of the trade chapter 9 is written to make measurable, and it costs 1.6 points of error to go from no look-ahead to a full second of it. Arithmetic: 7.0 - 5.4 = 1.6. |

### V-05-56 · Nemo Streaming Conformer Transducer Small Checkpoint

| Field | Value |
|---|---|
| status | `unresolved` |
| quantity | `nemo_streaming_conformer_transducer_small_checkpoint` |
| value | `` |
| unit | `n/a` |
| conditions | `searched for a checkpoint that is at once a Conformer-Transducer, streaming, and the Small variant, in the English score table `docs/source/asr/data/scores/en/conformer_en.csv`` |
| source_tier | `T2` |
| doc_id | `NeMo Conformer English Score Table` |
| title | NeMo docs/source/asr/data/scores/en/conformer_en.csv |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/6f20e61e4d11ce4dafc0f037c3bad535e1ac3ea9/docs/source/asr/data/scores/en/conformer_en.csv |
| locator | Absence across the whole file: line 1 is the header and lines 2 to 28 are its 27 data rows, every one of which was read. The only conformer_transducer rows are lines 9 to 14 and none of them is streaming, every streaming row in the file is a fastconformer hybrid, and no row names both small and streaming |
| quote |  |
| retrieved_utc | `2026-09-13T21:32:58Z` |
| access | `open` |
| corroborating_url |  |
| notes | Unresolved by rule 8, and deliberately narrower than 'no such model exists'. What was checked: this table, where NVIDIA publishes LibriSpeech results for the family, carries no such row; the recipe directory has no streaming Small config, only the four variants of the offline table at V-05-12; and the HuggingFace checkpoint catalogue could not settle it, because an anonymous request for the small model's repository answers HTTP 401, so absence from its listings proves nothing either way. The spine's phrase therefore has no published accuracy attached to it, which is the split C-08 records. |

### V-05-57 · Nemo Conformer Encoder Frame Cost

| Field | Value |
|---|---|
| status | `unresolved` |
| quantity | `nemo_conformer_encoder_frame_cost` |
| value | `` |
| unit | `n/a` |
| conditions | `three quantities of the target encoder, unresolvable from documentation alone` |
| source_tier | `T5` |
| doc_id | `n/a` |
| title | No primary source found |
| url |  |
| locator | plan-v2.md section 4.2 lists MACs per frame, INT8 weight bytes and activation bytes per frame as quantities the chapters may print; none has a source |
| quote |  |
| retrieved_utc | `2026-09-13T22:01:28Z` |
| access | `open` |
| corroborating_url |  |
| notes | No publisher prints these for a NeMo Conformer. They follow from the shapes now registered in V-05-12 to V-05-47 only once a counted parameter breakdown exists, which needs either the checkpoint itself, gated with HTTP 401 to an anonymous request, or a golden-model run over the recipe config. Until then chapters 8 and 9 may describe the datapath but cannot size it. Kept as one record because the gap is one decision, what to run, not three unrelated searches. |
