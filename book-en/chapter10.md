# Benchmarking, the Pareto Frontier, and Writing the Paper

> *Objective: Establish a fair experimental evaluation framework comparing NVIDIA Jetson Orin with FPGA platforms, analyze the multi-objective Pareto Frontier, and structure an academic manuscript.*

---

## The only thing that could end the argument, and how to make it end honestly

Everything before this chapter is a claim about what a migration would cost and what it would buy. This
is the chapter where claims stop mattering and a measurement takes their place. The book has spent nine
chapters arguing that a GPU built to chew enormous batches stalls when it is handed one frame at a time,
and that a fabric wired into the shape of the computation can keep that frame flowing. That argument is
not settled by being made well. It is settled by putting both boards on a bench, feeding both the same
audio, and writing down what each one did -- and if the numbers disagree with the argument, the numbers
win. This chapter is about earning numbers that would survive someone trying to disagree with them.

The first discipline is fairness, and it is harder than it sounds, because the two machines are not
naturally comparable. A watt on the Jetson is read out by an operating system that was never meant to be
a stopwatch, and it is a watt the board spent while its scheduler decided when to run you; a watt on the
fabric is a board you wired yourself, spending exactly what the logic in front of it draws. A millisecond
of GPU latency contains a queue you do not control; a millisecond on the fabric is a wire length and a
clock. The chapter lays out what has to be held identical -- the same audio, the same model quality bar, the same
power mode, the same definition of "done" -- before any difference is allowed to be called a result,
because a comparison where three things changed at once measures nothing.

The second is what to actually report, and the answer the book commits to is a small set of numbers that
trade against each other rather than a single winner: how long a frame takes, how much energy it costs,
how far behind real time the machine falls, and how good the task still is at the end. Chapter 2 defined
those quantities; this chapter is where they stop being definitions and become columns of a table. The
third is how to write it up so a reader can use the disagreement -- not "our board is better," which
nobody can check, but the shape of the result: the Pareto frontier of which machines are worth building
at all once you plot speed against energy, and the empty cells that still need a board to fill. This is
where every `unresolved` marker the rest of the book has been leaving behind becomes the actual work,
and where the book's central promise -- print the gap, name what would close it -- is finally cashed.

---

## 10.1 Principles of Fair Hardware Evaluation in Academic Research
## 10.2 The Multi-Dimensional Metric Matrix: Latency, RTF, Joules/Frame, and Task-Matched Quality
## 10.3 Constructing and Interpreting the Pareto Frontier
## 10.4 Structuring and Drafting a Paper for Top Hardware/Speech Conferences
