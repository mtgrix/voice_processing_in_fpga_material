# Preface {.unnumbered}

This book is about a move. A speech model runs on one board, and we want it on
another board that works in a completely different way. The first board is an
NVIDIA Jetson Orin, which is a small computer with a graphics processor. The
second is a Kria KV260, which is an FPGA: a chip you can rewire after it is
manufactured. Moving the model is not a software port. It changes what "fast"
means.

## The Journey of an Audio Frame

Before any part of that move is argued, the whole machine has to be in one view. The book
follows one object all the way through: a single frame of sound, from the air in front of a
microphone to a word on a screen. That object is the spine of the book, and every chapter
belongs to one of its six stages.

The six stages, in the order a frame meets them:

- **Air and microphone.** Sound is a pressure wave. A microphone turns the wave into a
   voltage, and an encoder turns the voltage into numbers. This is the stage where a
   "no microphone on this board" problem is decided, not discovered.
- **Sample stream.** The numbers arrive forever, at an even rate, one after another.
   Nothing here is a file. A design that waits for the recording to finish has already
   failed, because the recording does not finish.
- **DSP front end.** The stream is cut into overlapping frames, each frame is shaped by a
   window, turned into frequencies, compressed onto a scale that matches how the ear hears,
   and squashed into a small set of numbers per frame. This is signal processing, and its
   cost is measured in bytes per frame and in how often a frame is ready.
- **Model.** A trained network reads those numbers and produces a score over vocabulary
   items. This stage is a fixed recipe of multiply-accumulate operations, and the book
   needs the recipe only as arithmetic, never as a research topic. Appendix A is that
   detour, and nothing more.
- **Fabric logic.** The recipe is rebuilt as wiring: storage cells that hold a sliding
   window, arithmetic blocks that are placed rather than scheduled, and a clock period that
   has to close. This is where the move either pays or costs.
- **Output and latency.** A word appears, and the question stops being "how long did the
   compute take" and becomes "how long after the sound did the answer arrive, and how often
   does it miss". Latency is a property of the whole chain, which is why it is a stage
   rather than a chapter.

[Figure 1](#fig-master-pipeline) puts the six on one line, with the chapter that owns each
stage underneath, and marks the part of the chain this book moves.

::: {#fig-master-pipeline .figure}
```tikz
% The book's spine: one audio frame, six stages, and the chapters that own them.
% Everything to the right of the dashed line is what the project rebuilds in fabric.
\begin{tikzpicture}[
  font=\footnotesize,
  stg/.style={draw, align=center, inner sep=4pt, minimum width=1.85cm, minimum height=11mm},
  mob/.style={stg, fill=black!7},
  own/.style={font=\scriptsize, text=black!60, align=center, inner sep=0pt},
  arr/.style={-{Stealth[length=2.1mm]}, semithick}]
\node[stg] (a) at (0,0) {\textbf{1}\\ Air and\\ microphone};
\node[stg] (b) at (2.3,0) {\textbf{2}\\ Sample\\ stream};
\node[stg] (c) at (4.6,0) {\textbf{3}\\ DSP\\ front end};
\node[mob] (d) at (6.9,0) {\textbf{4}\\ Model};
\node[mob] (e) at (9.2,0) {\textbf{5}\\ Fabric\\ logic};
\node[mob] (f) at (11.5,0) {\textbf{6}\\ Output\\ and latency};
\draw[arr] (a) -- (b);
\draw[arr] (b) -- (c);
\draw[arr] (c) -- (d);
\draw[arr] (d) -- (e);
\draw[arr] (e) -- (f);
\node[own,anchor=north] at ($(a.south)+(0,-1.4mm)$) {ch. 6\\ ch. 8};
\node[own,anchor=north] at ($(b.south)+(0,-1.4mm)$) {ch. 4\\ ch. 8};
\node[own,anchor=north] at ($(c.south)+(0,-1.4mm)$) {ch. 1\\ ch. 6};
\node[own,anchor=north] at ($(d.south)+(0,-1.4mm)$) {App. A\\ ch. 7\\ ch. 9};
\node[own,anchor=north] at ($(e.south)+(0,-1.4mm)$) {ch. 4, 5\\ ch. 8};
\node[own,anchor=north] at ($(f.south)+(0,-1.4mm)$) {ch. 2, 3\\ ch. 10};
% The lower inset is sized by the label, not by the stage boxes: the Model box carries three lines
% of ownership (Appendix A, chapter 7, chapter 9), and two lines of inset clipped the third one.
\draw[densely dashed, black!55, rounded corners=2pt]
  ($(d.north west)+(-1.6mm,2.6mm)$) rectangle ($(e.south east)+(1.6mm,-15mm)$);
\node[above, text=black!65, align=center] at ($(d.north west)!0.5!(e.north east)+(0,2.4mm)$)
  {what the book moves:\\ the arithmetic, then the wiring};
\end{tikzpicture}
```
The dashed box is the thesis. Stages one to three are the same problem on both boards, and
stage four is the same mathematics on both; stage five is where an FPGA stops being a
smaller GPU and becomes a different kind of machine.
:::

Read the stage names again as a promise about the book. A reader who loses the thread in
chapter 8 can ask one question to get it back: which of the six stages is this? No section
in this volume is about more than one of them, and no stage is left to a chapter that does
not name it.

The stages also fix what each board has to be good at, which is the reason the move is hard.
On the Orin, the frame is handed to a general-purpose processor that fills itself by running
many frames at once. On the KV260, the frame is handed to wiring that is arranged in the
shape of the computation, so it never waits for a scheduler -- and never gets one either.
Stage by stage, the two columns below say what must be true at each stop, and where the book
argues it.

| Stage | What must be true here | Where the book argues it |
| --- | --- | --- |
| **Air and microphone** | A microphone exists, and its bits reach logic the project controls | chapter 8, whose first section is the board that has none, and chapter 6 |
| **Sample stream** | Samples arrive on time forever, with no copy that can block | chapter 4 for the crossing, chapter 8 for one second traced |
| **DSP front end** | Each frame becomes a fixed-size feature vector inside its own deadline | chapter 1 for the arithmetic, chapter 6 for accelerating it |
| **Model** | The arithmetic of the network is known: how many reads, how many multiplies | Appendix A, chapter 7 and chapter 9 |
| **Fabric logic** | The arithmetic fits in cells, tiles and slices, and the clock closes | chapter 4, chapter 5 and chapter 8 |
| **Output and latency** | The answer arrives after the sound, and the gap is measured, not assumed | chapter 2, chapter 3 and chapter 10 |

The book grew out of a learning project, and it kept the shape of one. Every
number in it comes from a record in `docs/verification/claims.json`. Each record
names the document the number came from, the page, and the exact sentence. When
a number has no such record, this book does not print it as a fact. It prints the
gap instead, and says what would close it.

That rule produces an odd-looking book in places. A table may have an empty
cell. A conclusion may be written as a method: "to find out, measure this, then
compare it to that". We chose this on purpose. A reader of a hardware book needs
to know which numbers are printed in a datasheet, which are computed from
printed numbers, and which nobody has measured yet. A book that hides those three
categories teaches a method that does not exist.

## What this book is not

It is not a report of results. The project has no board on a bench. There is no
latency table here that anyone measured, because nobody has measured one. Where
results would go, you will find the shape of the measurement: what to log, what to
hold fixed, and what to compare it against. When a board arrives, the numbers
fill the shape, and nothing else has to be rewritten.

It is not a survey of related work either. Chapter 10 explains how to write up a
result for a conference, because that is part of doing the work properly. It does
not review the literature on behalf of someone who has read it.

## How to read the empty cells

An empty cell is a claim about the world that we have not earned. It is not a
placeholder waiting for any number. `docs/WEB_SEARCH_PROTOCOL.md` is the rulebook
for earning one, and its central rule is simple: a number enters the book only
from a named page of a named document, or from a log file that a script produced
and a checksum names.

Three chapters carry a ridge point, a roofline, or a resource table. Each of
them tells you which part is printed, which part is arithmetic, and which part is
an assumption with a label on it. Read those labels as content, not as apologies.

## How the maths is written in this book

Every formula in this volume is printed as a card with five labelled parts: the formula, the
variables, what it means, what it costs in silicon, and what it does not say. The last part is
not decoration. A formula that a reader trusts too widely is the most expensive kind of error
in a hardware design, because it is correct right up to the edge of an assumption nobody wrote
down.

The rule that produces the cards is `docs/BOOK_PEDAGOGY.md` section 7, and it exists because
the book's reader is assumed to be a hardware engineer. That reader can size a power rail,
count BRAM tiles and close a timing report without help, and is not obliged to know what a
softmax is. Nothing in the machine-learning part of the chain is treated as common knowledge,
and nothing is treated as too far from the argument to explain.
