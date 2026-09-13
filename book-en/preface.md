# Preface {.unnumbered}

This book is about a move. A speech model runs on one board, and we want it on
another board that works in a completely different way. The first board is an
NVIDIA Jetson Orin, which is a small computer with a graphics processor. The
second is a Kria KV260, which is an FPGA: a chip you can rewire after it is
manufactured. Moving the model is not a software port. It changes what "fast"
means.

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
