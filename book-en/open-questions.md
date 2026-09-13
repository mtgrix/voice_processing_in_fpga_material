# Open Questions and Open Numbers {.unnumbered}

This chapter is a list of what the book does not know. It is last on purpose.
Every item names the evidence that would close it, and where that evidence would
have to be written down. A reader who finishes the book with a board on a bench
should be able to work through this page and turn each line into a record.

## The one that changes other answers

The project has not registered which Jetson Orin it measures against. That record
is `V-02-28`, and its status is `unresolved` with no value: the question was never
answered in the evidence set, only asked.

This is not a detail. A ridge point, which is the memory bandwidth a processor can
feed divided into its peak compute, depends on both numbers, and Orin models differ
in both. The book's worked example is `V-07-02`, whose own conditions line reads
"Jetson Orin NX 16GB at the MAXN profile: 50 TOPS dense / 100 TOPS sparse,
102 GB/s memory bandwidth", giving 490.2 OP/byte dense and 980.4 OP/byte sparse.

The smallest current dev kit in the family is the Orin Nano Super, which is the
board a reader is most likely to own. Three verified records describe it:

| Record | Value | What it is |
| --- | --- | --- |
| `V-02-09` | 67 | Sparse INT8 TOPS, Orin Nano Super Developer Kit |
| `V-02-10` | 102 GB/s | LPDDR5 bandwidth, 128-bit at 3199 MHz |
| `V-02-31` | 2x | NVIDIA's stated throughput factor for 2:4 structured sparsity |

Dividing those gives a sparse ridge point near 660 OP/byte, and about half that,
near 330, for dense INT8. Those two results are **arithmetic in this book, not a
vendor figure**, and no record carries them. The gap they expose is real: a
Super-based Orin side of the comparison sits roughly a third of the way up from
the NX-based one, and the whole point of the roofline argument shifts with it.
Closing this means a fetched datasheet page for the specific SKU, registered as
its own record, not a recalculation of these numbers.

`V-07-02` is not wrong and was not edited. It names its SKU in its conditions,
which is exactly what a good record does. What is missing is its partner.

## Numbers the project cannot produce yet

Nothing here has a board behind it. Each row is a measurement, not a search.

| Open item | Record | What closes it |
| --- | --- | --- |
| Latency, RTF and energy per frame on Orin | — | A run on the device, with a checksummed log per row |
| The same three on KV260 | — | A run on the device, same rules |
| The achievable DSP clock behind `V-07-03` | `V-07-03` | A synthesis report for a real design, not a datasheet |
| Which board is actually purchased | `V-02-28` | A decision, then a datasheet fetch |
| Board pricing | `V-03-04` | Price pages are corroborating only; they never become a verified quantity |
| Which DPU rung the factory image loads | `V-04-13` | Reading the image itself on hardware |
| Published FPGA keyword-spotting results to compare with | `V-07-05` | A related-work pass with per-paper extraction |

`V-07-03`'s 39.0 to 78.0 OP/byte is the FPGA side of the comparison in chapter 3.
It rests on a 300 MHz clock that is an assumption, and the result is proportional
to it: at 500 MHz the pair becomes 65.0 and 130.0. The sensitivity is printed
beside the number, in the record and in the chapter, because an unlabelled
assumption in a numerator is the most expensive kind of error in this field.

## Records that disagree with themselves

Three records carry `conflict`, which means two printed values exist and both are
kept. Four carry `unresolved`, which means the question stands with no answer.

| Status | Records |
| --- | --- |
| `conflict` | `V-01-11`, `V-02-33`, `V-04-04` |
| `unresolved` | `V-02-28`, `V-03-04`, `V-04-13`, `V-07-05` |

`V-02-33` is the instructive one: one vendor document, three pages, two answers for
the same engine's throughput. Read it as a lesson about where datasheet numbers are
generated, not as a mistake to average away.

## What the book's own apparatus cannot check yet

These are gaps in the machinery, and they are measurable right now, so they are
stated as measured rather than estimated, and the count is reproducible: each row below is a
`grep --count` of the named pattern over the named set, taken on 2026-09-13 after
Issue #42 made `book/references.bib` a rendering of the registry. Records and sources are read out of
`docs/verification/claims.json`; references are occurrences of `V-` plus two digits, a hyphen,
the next two digits, in `book-en/chapter*.md`, counting repeats, because a chapter that names
the same record twice cited it twice.

| Fact about this manuscript | Count |
| --- | --- |
| Records in the evidence set | 103 |
| Of those, `verified` | 96 |
| Distinct sources the records cite | 41 |
| Entries in `book/references.bib` | 30 |
| Sources the registry answers a label for | 33 |
| Citation markers written into the manuscript | 0 |
| Record references appearing in a chapter body | 17 |
| Figures of any kind | 0 |
| Numbered section headings across the ten chapters | 39 |
| Of those, sections still without prose | 34 |

The middle rows are one story told twice, and the telling matters. Chapter 1
quotes 13 records in its body, 17 times over, in the `V-xx-yy` form that points
into `docs/verification/claims.json`. That is not a citation marker, which is the
at-sign-and-key form in square brackets, and the text still holds none of those.
The identifier gap that used to sit behind that sentence is closed: the
bibliography is now generated from the same 30 registry rows the evidence records
resolve against, and a chapter cites one by its registry id, so a marker naming `S009`
and the `doc_id` of the quote that established a number name the same document. What is
left is the writing. The build gate therefore still reports its bibliography checks
as **N/A**, not as passed, because a check that found nothing to check is not
evidence of health -- and a record reference is not a citation: it names where a
number was read, not a work in the list at the back.

The same applies to figures. There is no diagram in this book, so no figure
renderer is wired into the build. Adding Mermaid or TikZ stages before a figure
exists would produce a pipeline that tests itself.

## Order of work, if a reader wants to help

1. Register the board decision, then fetch the datasheet page for that SKU.
2. Write citations into the prose as claims are made. The reconciliation is done:
   the entries are generated, so a citation is a registry id and nothing else.
3. Draft prose under the 34 section stubs that remain, one chapter at a time.
4. Draw the two figures that the roofline argument genuinely needs, then wire a
   renderer.
5. Run the experiments in `chapterNN/` on real hardware and fill the empty cells.

Step 5 is the one this project cannot do alone, and it is the reason this chapter
exists at all.
