# Verification Records: 03 Kv260 Audio Path

### V-03-01 · Kv260 Onboard Audio Hardware

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `kv260_onboard_audio_hardware` |
| value | `None` |
| unit | `n/a` |
| conditions | `KV260 carrier card` |
| source_tier | `T2` |
| doc_id | `UG1089 (v1.4)` |
| title | Kria KV260 Vision AI Starter Kit User Guide |
| url | https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit |
| locator | p.5, Product Details Table; p.17 Chapter 4 Table 5 |
| quote | Audio transmit and receive (I2S) via PMOD audio codec |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit |
| notes | KV260 carrier card has no onboard microphone, audio jack, or audio ADC/DAC. Audio input requires an external add-on module via PMOD or USB. |

### V-03-02 · Kv260 Official Audio Pmod Peripheral

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `kv260_official_audio_pmod_peripheral` |
| value | `Digilent PMOD SKU 410-379` |
| unit | `string` |
| conditions | `Tested with KV260 Smart Camera accelerated application via PMOD J2` |
| source_tier | `T2` |
| doc_id | `UG1089 (v1.4)` |
| title | Kria KV260 Vision AI Starter Kit User Guide |
| url | https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit |
| locator | p.17, Table 5 'Accelerated Application Peripherals', row 'Smart camera / Audio Codec I2S PMOD (J2)' |
| quote | Smart camera \| Audio Codec I2S PMOD (J2) \| Digilent PMOD SKU 410-379 |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://digilent.com/shop/pmod-i2s2-stereo-audio-input-and-output/ |
| notes | Plugs into PMOD connector J2 on the KV260 carrier card. |

### V-03-03 · Pmod I2S2 Codec Ics

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `pmod_i2s2_codec_ics` |
| value | `Cirrus CS5343 A/D and CS4344 D/A` |
| unit | `string` |
| conditions | `Digilent Pmod I2S2 Revision A, 24-bit resolution, stereo line in and line out` |
| source_tier | `T2` |
| doc_id | `Pmod I2S2 Reference Manual` |
| title | Digilent Pmod I2S2 Reference Manual |
| url | https://media.digikey.com/pdf/Data%20Sheets/Digilent%20PDFs/Pmod_I2S2_RM_Web.pdf |
| locator | p.1, Overview, paragraph 1 |
| quote | The Digilent Pmod I2S2 (Revision A) features a Cirrus CS5343 Multi‐Bit Audio A/D Converter and a Cirrus CS4344 Stereo D/A Converter, each connected to one of two audio jacks. These circuits allow a system board to transmit and receive stereo audio signals via the I2S protocol. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://digilent.com/shop/pmod-i2s2-stereo-audio-input-and-output/ |
| notes | Supports input sample rates up to 108 kHz and output sample rates up to 200 kHz. |

### V-03-04 · Pmod I2S2 Price Usd

| Field | Value |
|---|---|
| status | `unresolved` |
| quantity | `pmod_i2s2_price_usd` |
| value | `` |
| unit | `string` |
| conditions | `Retail distributor pricing (Digilent, DigiKey, Mouser)` |
| source_tier | `T4` |
| doc_id | `Digilent Product Catalog` |
| title | Digilent Pmod I2S2: Stereo Audio Input and Output |
| url |  |
| locator | Product purchase page |
| quote | Pmod I2S2: Stereo Audio Input and Output SKU: 410-379 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://www.digikey.com/en/products/detail/digilent-inc/410-379/9445907 |
| notes | NOT EVIDENCED: the previous quote ('Pmod I2S2: Stereo Audio Input and Output SKU: 410-379') contains no price, so the recorded range 19.99-24.99 USD had no source inside the record. Re-fetch of the Digilent product page on 2026-09-12 returned HTTP 403 Forbidden. A retail price is volatile and a vendor product page is T4, which protocol rule 2 does not admit as a sole source. Get a distributor order-page quote (DigiKey / Mouser) or reclassify this as a BOM decision rather than a verification record. The PMOD I2S2 part number itself stays evidenced by V-03-02 and V-03-03. |

### V-03-05 · Kv260 Usb Audio Alternative

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `kv260_usb_audio_alternative` |
| value | `4x USB 3.0 Type-A interfaces` |
| unit | `ports` |
| conditions | `KV260 carrier card USB host controller` |
| source_tier | `T2` |
| doc_id | `DS986 (v1.1)` |
| title | Kria KV260 Vision AI Starter Kit Data Sheet |
| url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit |
| locator | p.6 Table Specification, row 'USB3.0 interface' |
| quote | USB3.0 interface: x4 |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit |
| notes | Provides standard Linux ALSA UAC1/UAC2 audio capture via USB microphones without requiring carrier modification. |
