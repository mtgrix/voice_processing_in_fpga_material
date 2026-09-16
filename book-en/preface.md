# Preface {.unnumbered}

Somebody says one word. This book is about what happens between that word and a machine knowing it,
on two machines that disagree about almost everything, including what the word *ready* means.

The two machines are an NVIDIA Jetson Orin and a Kria KV260. The Orin is a small computer with a
graphics processor in it, and it is good at its job for a reason: it owns a **scheduler**, an
admissions desk that decides which work runs next. The KV260 is a field-programmable gate array
(FPGA -- a chip you can rewire after the factory has finished it), and it has no scheduler at all.
Nothing decides anything on it. Whatever happens, happens because a piece of wiring was built to make
it happen.

That asymmetry is the whole difficulty of this book, and it cuts both ways. This is not a story about
one chip being faster than another.

## The machine that waits

A graphics processor is a very wide bench of arithmetic lanes that all obey one instruction at a time.
Its speed comes almost entirely from having all of them busy on the same instruction at the same
moment. One frame of speech audio is not enough to fill the bench, and an unfilled bench is a bench
being paid to stand still.

So the machine gathers. It holds the first frame back until enough frames have arrived to fill it, and
then it works on the whole group at once. The group is a **batch**, and the number of items in it is
the batch size. Gathering is not a flaw in the design; it is the design. A batch of eight means the
frame at the front of the line waits while seven more are collected, and the wait is not small. This
book's frame period is ten milliseconds -- chapter 1 shows where that number comes from -- so seven
frame periods is seventy milliseconds of a person waiting for an answer.

There is a second cost that hides behind the first. Because an admissions desk exists, it can let
other work through ahead of yours. A frame that arrives at the Orin joins a queue, and the length of
that queue is not a property of your program. It is a property of everything else the board is doing
at the time: the microphone driver, the network stack, the model. This is where jitter comes from, and
jitter -- answers that sometimes come late, rather than always coming late -- is the specific thing a
streaming voice system can least afford.

What the Orin is genuinely excellent at deserves saying too, because otherwise this reads like
marketing for the other chip. A batch makes its arithmetic lanes full, and full lanes are cheap lanes.
If you can wait, a graphics processor does more work per joule with almost no engineering effort,
because the scheduler solves your scheduling problem for you.

## The machine that is built

An FPGA asks for the trade in the other direction. You do not hire a crew and keep it busy. You build a
row of machines, wire each one to do a single step, and bolt them together in the order the arithmetic
needs. Then the data goes through them like water through pipes: a sample enters at one end, an answer
leaves at the other, and at any instant several items are in the pipes simultaneously at different
steps. Nobody gathers anything, because nothing has to be gathered. The wiring is the plan.

The gain is exact, and it is the reason anyone puts up with this. There is no admissions desk, so
nothing can be waved through ahead of you. Your work is not in a queue; it is in a piece of copper. A
deadline on an FPGA is not enforced by a scheduler being polite about your priority -- it is enforced
by whether the arithmetic finishes inside one clock period, which either holds or it does not, and you
find out before the board is built rather than in a demonstration.

The price is equally exact. To wire a thing, you have to know its shape in advance, in physical
detail: how wide every number is, how many of them arrive together, where the values live between one
step and the next, and what the wiring does when a value has not arrived on time. Every one of those is
a decision you must make *before* the design exists, and a decision you cannot reverse cheaply
afterwards. A crew can be told to do something different tomorrow. A row of specialised machines
cannot be told anything; it has to be taken apart. A program that changes its mind about the shape of
its arithmetic -- a different model, a different frame length, a new layer -- is not a small edit on
this machine. It is a rebuild.

[Figure 1](#fig-two-readiness) puts the two on one time axis, because the disagreement is easier to see
than to say. Read it as the argument of the whole book: the upper band is the same computation the lower
band performs, and the only thing that differs is *when the work is allowed to start*.

::: {#fig-two-readiness .figure}
```tikz
% The two machines on ONE shared time axis, measured in frame periods. The faint vertical grid is
% that shared clock, so the comparison happens where the machines actually differ -- in time.
% Upper band gathers a batch, computes nothing while it waits, then answers in one burst. Lower band
% is a space-time diagram: each rectangle is one frame sitting in one wired step for one period, and
% the frames lie on diagonals because a frame entering at period zero reaches step four at period
% three. Nothing is gathered, so an answer leaves on every period.
% Geometry only. One unit (cm); x(p) = X + p*P for period p. Vertical budget, top to bottom:
% upper title 4.55 | inputs 4.08 | "arriving" 3.74 | hold+job band 3.22 | burst note 2.86 |
% lower title 2.02 | frame labels 1.74 | step rows 1.52,1.18,0.84,0.50 | output lane 0.06 |
% axis -0.52. Cell pitch (0.34) exceeds cell height (0.30) so step rows never touch, and the output
% lane clears step four by 0.15cm, so no answer square overlaps a cell.
\begin{tikzpicture}[
  font=\tiny,
  inb/.style={draw=black!70, thin, fill=black!10, inner sep=0pt,
              minimum width=4.0mm, minimum height=4.0mm},
  hold/.style={draw=black!45, thin, densely dashed, fill=black!3, inner sep=1pt, align=center,
               minimum height=6.2mm, text=black!74},
  job/.style={draw=black!72, semithick, fill=black!9, inner sep=1pt, align=center,
              minimum height=6.2mm},
  cell/.style={draw=black!62, thin, fill=black!14, inner sep=0pt,
               minimum height=3.0mm},
  outb/.style={draw=black!70, thin, fill=black!50, inner sep=0pt,
               minimum width=2.8mm, minimum height=2.8mm},
  ann/.style={font=\tiny, text=black!66, align=center, inner sep=0pt},
  annt/.style={font=\tiny, text=black!66, align=left, inner sep=0pt},
  ttl/.style={font=\tiny\itshape, text=black!78, align=left, inner sep=0pt},
  stl/.style={font=\tiny, text=black!72, anchor=east, inner sep=1pt},
  tk/.style={font=\tiny, text=black!56, anchor=north},
  gd/.style={black!13, thin},
  ar/.style={-{Stealth[length=1.3mm]}, black!58, thin}]
\def\P{0.98}   % cm per frame period
\def\X{1.72}   % cm, left edge of period zero (leaves the step-label column clear)

% ---------- shared period grid ----------
\foreach \p in {0,...,12} {
  \draw[gd] (\X + \p*\P,-0.34) -- (\X + \p*\P,3.58);
}

% ---------- upper band: gather, then go ----------
\node[ttl, anchor=west] at (0,4.55) {the machine with a scheduler};
\foreach \f in {0,1,2,3} {
  \node[inb] at (\X + \f*\P + \P/2,4.08) {};
}
\node[annt, anchor=north west] at (\X,3.74) {frames arriving, one per period};
% holding: the first frame waits while the batch fills, so nothing computes until period four
\draw[hold] (\X,2.97) rectangle (\X + 4*\P,3.47);
\node[ann] at (\X + 2*\P,3.22) {nothing computes\\while it waits};
\draw[ar] (\X + 4*\P + 0.06,3.22) -- (\X + 4*\P + 0.30,3.22);
% one pass over the whole batch -- length drawn to be readable, not measured
\draw[job] (\X + 4*\P + 0.36,2.97) rectangle (\X + 6*\P + 0.36,3.47);
\node[ann] at (\X + 5*\P + 0.36,3.22) {one pass over\\the whole batch};
\draw[ar] (\X + 6*\P + 0.42,3.22) -- (\X + 6*\P + 0.66,3.22);
\foreach \k in {0,1,2,3} {
  \node[outb] at (\X + 6*\P + 0.84 + 0.32*\k,3.22) {};
}
\node[annt, anchor=north west, text=black!82] at (\X + 6*\P + 0.66,2.88)
  {all four answers at once,\\then silence until the\\next batch fills};

% ---------- lower band: wired, so it flows (space-time diagram) ----------
\node[ttl, anchor=west] at (0,2.02) {the machine that is wired};
\foreach \j in {0,1,2,3} {
  \pgfmathsetmacro{\yy}{1.52 - 0.34*\j}
  \node[stl] at (\X - 0.10,\yy) {step \the\numexpr\j+1};
}
% frame f occupies step j during period f+j; one cell per (period, step), with a small side gap
\foreach \f in {0,1,2,3} {
  \foreach \j in {0,1,2,3} {
    \pgfmathsetmacro{\cx}{\X + (\f+\j)*\P + \P/2}
    \pgfmathsetmacro{\cy}{1.52 - 0.34*\j}
    \node[cell, minimum width=\P cm - 0.12cm] at (\cx,\cy) {};
  }
}
\foreach \f in {0,1,2,3} {
  \pgfmathsetmacro{\cx}{\X + \f*\P + \P/2}
  \node[ann, text=black!55] at (\cx,1.74) {$f_{\f}$};
}
% an answer leaves step four one period after each frame enters: periods four to seven, on their own
% lane below the grid, so no square sits on a cell
\foreach \f in {0,1,2,3} {
  \pgfmathsetmacro{\cx}{\X + (\f+4)*\P + \P/2}
  \node[outb] at (\cx,0.06) {};
}
\draw[ar] (\X + 8*\P + 0.30,0.06) -- (\X + 8*\P + 0.72,0.06);
\node[annt, anchor=west, text=black!82] at (\X + 8*\P + 0.78,0.06)
  {one answer per period,\\for as long as the board is powered};

% ---------- the shared axis ----------
\draw[->, black!72] (\X,-0.52) -- (\X + 12*\P + 0.30,-0.52);
\node[ann, anchor=west] at (\X + 12*\P + 0.36,-0.52) {time};
\foreach \p in {0,...,12} {
  \draw[black!50] (\X + \p*\P,-0.555) -- (\X + \p*\P,-0.485);
  \node[tk] at (\X + \p*\P,-0.58) {\p};
}
\node[annt, text=black!58] at (\X + 9.4*\P,-1.06) {frame periods};
\end{tikzpicture}
```
The faint vertical lines are shared by both bands, so the two machines are read against the same
periods. In the upper band the first four periods hold no computation at all -- the machine is waiting
for a batch -- and when answers do come they come together, after which the band is empty until the next
group fills; in the lower band each rectangle is one frame in one wired step for one period, the frames
lie along diagonals, and because nothing is gathered an answer leaves on every period. What the figure
is built to show is the *shape* of the output -- a burst against a stream -- and that shape does not
depend on any timing this book has not measured. The one length drawn as a choice is the width of the
compute box in the upper band; the rest is a fact about ordering, not about speed, which is that the
batched machine cannot answer before its batch has arrived while the wired machine answers on the period
after a frame enters.
:::

## The journey of an audio frame

A trade this sharp is not something anyone should try to hold in their head at once, so the book does
not. It takes the machine apart along the one axis that makes the pieces independent: the path a single
frame of sound travels. Sound is a pressure wave in the air. A microphone turns the wave into a
voltage, and an encoder turns the voltage into numbers. From then on the numbers are the word, and they
pass through a fixed sequence of stages until one of them becomes a decision on a screen.

The book follows that object all the way through, and every chapter belongs to one of its stages. The
stage names below are used verbatim everywhere in the volume, so a reader who loses the thread anywhere
can ask one question to get back: **which stage is this?**

- **Air and microphone.** A pressure wave becomes numbers. This is the stage where a "there is no
   microphone on this board" problem is decided rather than discovered.
- **Sample stream.** The numbers arrive forever, at an even rate, one after another. Nothing here is a
   file, and a design that waits for the recording to finish has already failed, because the recording
   does not finish.
- **DSP front end.** The stream is cut into overlapping frames, each frame is shaped by a window,
   turned into frequencies, compressed onto a scale that matches how the ear hears, and squashed into a
   small set of numbers. This is signal processing, and its cost is bytes per frame.
- **Model.** A trained network reads those numbers and returns a score for each thing it recognises. To
   this book the network is a fixed recipe of multiply-and-add steps, and the appendix is the only
   detour that recipe gets.
- **Fabric logic.** The recipe is rebuilt as wiring: storage cells that hold a sliding window,
   arithmetic blocks that are placed rather than scheduled, and a clock period that has to close. This
   is where the move either pays or costs.
- **Output and latency.** A word appears. The question stops being how long the compute took and
   becomes how long after the sound the answer arrived, and how often it misses. Latency is a property
   of the whole chain, which is why it is a stage and not a chapter.

[Figure 2](#fig-master-pipeline) puts the six on one line, with the chapters that own each stage
underneath, and marks the part of the chain this book moves.

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
The dashed box is the thesis. The first three stages are the same problem on both boards, and the model
stage is the same mathematics on both; the fabric stage is where an FPGA stops being a smaller graphics
processor and becomes a different kind of machine.
:::

## How this book cuts the problem

The cut above is not only a description of a machine. It is the method. A migration this size is
unmanageable as one question, because "is an FPGA better for speech?" cannot be answered, so the book
refuses to answer it and works through a sequence of smaller questions instead, one per stage or one
per pair of stages. Each of those can be checked without waiting for the chapters around it.

**What the two boards are, before anyone claims anything.** A migration needs a starting line and a
finish line, and neither can be taken on trust. The chapter on the Jetson Orin works out what the
baseline actually is: not its marketing rating, but what a specific board in a specific power mode does
to a specific frame, and how you would have to measure it to be believed. The chapter on the graphics
processor's streaming bottleneck then makes the case that this baseline's number is quoted in a
quantity the task does not use, which turns the Orin side of the trade above into arithmetic.

**What a frame is, and what it costs to make one.** The first chapter takes the front end apart: how a
stream becomes eighty numbers, what each step of that reduction actually does to the data, and where
the deadline comes from. Its companion chapter does the same reduction again, this time as hardware
somebody would have to synthesise. Between them sits the chapter on the FPGA's own interior -- logic
cells, multiplier blocks, on-chip storage -- because wiring cannot be reasoned about in the abstract. It
has to be counted in parts.

**What the network is made of, and how far it can be squeezed.** An appendix reads a trained model as
pure arithmetic: how many numbers it reads, how many it multiplies, and which of the two is the limit.
The methodology chapter then asks the question a hardware engineer actually faces, which is not which
model is most accurate but which of four ways of building one suits a job at all. And the quantization
chapter takes up the narrowest of the three trades in this book: an eight-bit number is cheaper than a
sixteen-bit one, in wires and in joules and in bytes moved, and it is also wrong in a way the model has
to survive.

**The two designs, and the disagreement between them.** The board-level chapter builds a keyword
spotter end to end, from a microphone the target board does not have, through a frame, to an answer. The
streaming chapter builds the harder one: a model that reads history, where the history has to be kept
somewhere, and where keeping it is most of what makes a batch of one so expensive on a machine built
for batches. The last chapter is about the only thing that could settle the argument -- a measurement
-- and about writing one up so that a reader can disagree with it usefully.

That ordering is a building order, not a viewing order. A reader needs a frame before a place to put it,
which is why the front-end chapters come before the fabric chapter even though the fabric is the
destination. The map above keeps the two straight, and its stage labels are printed rather than
described so that the order of the book and the order of the machine cannot drift apart.

**The first tier is a wake-word listener.** It is the only part of the pipeline that never switches off: one always-listening microphone path, whose whole job is to answer a single question -- is anyone speaking. It does not decide what was said, it does not transcribe, and it does not even keep the audio; it opens the gate for the tier above it. Because it owns every second of the day, its budget is set by patience rather than by speed, so it has to be tiny: well under one milliwatt, and a few tens of thousands of parameters at most.

**The second tier is a keyword spotter.** This is the board-level design the migration chapters build end to end: an acoustic model of under a hundred thousand parameters that listens for a closed vocabulary and decides which word from that set was said. It runs only after the first tier has already reported a voice, which is a small share of any hour -- call it about five per cent -- and while it runs it draws a few tens of milliwatts.

**The third tier is the transcriber.** This is the streaming recogniser family the book actually ports, and it is the expensive one: hundreds of milliwatts while it works, because it has to keep its own history somewhere and read it back on every step. But it works for the smallest fraction of the time of all three tiers, well under five per cent, so its share of the average bill is tens of milliwatts rather than hundreds.

**The arithmetic, said plainly.** Those three budgets are this book's own planning estimates, derived from the records the later chapters cite rather than read off a bench; no record cited anywhere in these pages says a build on this board will hit any of them. They are printed so that a reader can disagree with each one separately, and so that a later measurement has something to be measured against. The tiers exist at all because an always-on pipeline pays for its silence: a machine that keeps a transcriber awake to hear nothing spends the whole budget on the nothing.

[Figure 3](#fig-tier-power-staircase) puts the three budgets in one picture, and the picture is the argument.

::: {#fig-tier-power-staircase .figure}
```tikz
% A staircase of three tiers: each step is as wide as the share of time its tier runs,
% and as tall as that tier's operating power. The first tier spans the whole width
% because it never sleeps; the third is the narrow slice at the right, where the
% transcriber earns its keep. Heights are this book's planning estimates.
\begin{tikzpicture}[
  every node/.style={font=\scriptsize, align=center, text width=24mm},
]
\draw[->] (0,0) -- (8.8,0) node[below=3pt] {share of the time the tier runs};
\draw[->] (0,0) -- (0,4.1) node[left=3pt, align=center] {operating\\power};

\draw[fill=black!8]  (0,0)     rectangle (8.0,1.0);
\draw[fill=black!18] (3.4,1.0) rectangle (6.6,2.2);
\draw[fill=black!30] (5.8,2.2) rectangle (7.6,3.3);

\node at (4.0,0.5)  {wake-word listener\\ well under 1 mW\\ all of the time};
\node at (5.0,1.6)  {keyword spotter\\ a few tens of mW\\ about 5\% of the time};
\node at (6.7,2.75) {transcriber\\ hundreds of mW\\ well under 5\% of the time};
\end{tikzpicture}
```
The three tiers drawn as a power staircase. The wake-word listener is on for all of the time and costs the least; the transcriber costs the most and runs for the smallest share of it, so the wide low step sets the bill and the narrow high one does not.
:::

## What this book is, and what it is not

It is not a report of results. The project has no board on a bench. There is no latency table here that
anyone measured, because nobody has measured one. Where results would go, this book prints the shape of
the measurement instead: what to log, what to hold fixed, and what to compare it against. When a board
arrives, the numbers fill the shape and nothing else has to be rewritten.

That is an uncomfortable thing to publish in a hardware book, and the alternative was worse. Every
number in these pages comes from a record in `docs/verification/claims.json`, and each record names the
document the number came from, the page, and the exact sentence. When a number has no such record, the
book does not print it as a fact. It prints the gap, and says what would close it. So a table may have
an empty cell, and a conclusion may be written as a method. A reader of a hardware book needs to know
which numbers are printed in a datasheet, which are computed from printed numbers, and which nobody has
measured yet -- and a book that hides those three categories teaches a method that does not exist.

An empty cell is a claim about the world that has not been earned; it is not a placeholder waiting for
any number. `docs/WEB_SEARCH_PROTOCOL.md` is the rulebook for earning one, and its central rule is that
a number enters the book only from a named page of a named document, or from a log file a script
produced and a checksum names. Chapter 10 is where filling those cells becomes the work.

## How the maths is written here

This book assumes the reader is a hardware engineer, which means it assumes you can size a power rail,
count storage tiles and read a timing report without help -- and it assumes nothing at all about
machine learning. Nothing in the network half of the chain is treated as common knowledge, and nothing
is treated as too far from the argument to explain.

The harder assumption is the mathematical one, and it is stated plainly because it governs every formula
in the volume: **a formula is not explained by being labelled.** Listing what each letter stands for
gives you the vocabulary, not the sentence. So every printed formula here is a card with five parts, in
this order -- the formula, the variables, what it means, what it costs in silicon, and what it does not
say -- and the third part carries an obligation that is easy to skip and hard to satisfy by accident. It
must explain why the operations are the ones written.

What that means in practice is worth an example, because it is the difference between a book you can
read and a book you can only consult. Take $a = v/dt$, where $v$ is a change in velocity and $dt$ is a
thin slice of time. Naming the letters tells you nothing. The reason is this: acceleration answers "how
fast is velocity climbing", and anything that answers a *per unit* question has to be divided by the
unit -- divide a change in speed by the slice it took, and you are left with speed gained per slice,
which is exactly what the question asks for. Multiply instead, and the quantity you get grows when you
look at a longer slice, which is the opposite of a rate: it depends on how long you waited to measure
it. That is why a ratio, and not a product, is the only thing that can mean "how fast". Every card in
this book owes its reader an argument of that kind, and where the argument is long, it is long: a single
formula earns three pages if the reader would otherwise accept it on trust.

The last part of the card exists because a formula a reader trusts too widely is the most expensive kind
of error in a hardware design. An equation is correct right up to the edge of an assumption nobody wrote
down, and it fails at exactly the point where the assumption stops being true -- which is usually the
point where the board is already built.

Diagrams carry the same obligation as the cards. A concept that has a shape gets drawn, because
describing a shape in words makes the reader reconstruct it in their head, which is precisely the work a
picture exists to remove. A buffer that slides, a wave cut into overlapping frames, a matrix mostly made
of zeroes, a resource chart, a trade-off between two curves -- each of these is a picture in this book,
and the prose beside it points at the picture rather than restating it.
