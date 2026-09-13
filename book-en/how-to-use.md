# How to Use This Book {.unnumbered}

Ten chapters, in one order, on one system. Each chapter assumes the one before
it. Read straight through the first time. After that, a chapter can be read
alone if you know what its records are.

## The shape of a chapter

Each chapter opens with an objective: the thing you will be able to do at the
end. Then sections build one argument. Most sections end in the same two places:

* **A record reference**, such as `V-07-02`. This points into the evidence file,
  which holds the source document, the page, and the quoted sentence.
* **An experiment**, in the matching `chapterNN/` directory. An experiment is
  small and runnable, or it is written as a procedure with its result cells left
  empty.

The manuscript is a skeleton while its chapters are drafted, so most of it
does not yet carry the first of those two. Chapter 1 does: as of 2026-09-13 it
cites 15 record references in its body, and the other nine chapters cite none.
A `V-xx-yy` reference is not a bibliography citation, and the book currently has
none of those either, which is why the build gate reports its bibliography checks
as N/A rather than as passed. The ten `chapterNN/` directories do exist. The back
matter names the counts, and the build gate reports them rather than hiding them.

## Reading a record id

`V-07-02` means: section 07 of the evidence set, record 02. The section number
matches the chapter that uses it, not always the chapter that cites it.

| Status in a record | Meaning |
| --- | --- |
| `verified` | A named page of a named source prints this value, and a quote is stored. |
| `conflict` | Two sources, or two pages of one source, print different values. Both are kept. |
| `unresolved` | The question is real, and nobody has answered it yet. No value is claimed. |

`conflict` is not a failure. A `conflict` record usually carries a table showing
each reading and what each one costs. Read those records closely: they teach
where vendor numbers come from, which is the part a datasheet PDF cannot teach.

## Where the numbers are not

Some tables are half empty, and some are marked "not measured". Three things
must stay true while you read them:

1. A measured figure names the log file it came from. No log, no figure.
2. A figure from a datasheet names the document and the page.
3. A figure derived by arithmetic shows its inputs, so you can redo it.

If you find a number in this book that does none of the three, that is a defect.
Say so, and it becomes an Issue.

## Terms

A technical term is kept in English on first use and explained in plain English
in the same sentence or the next. `docs/GLOSSARY.md` is the term registry the
chapters are written against; there is no printed glossary in this volume yet. If
you meet a term used without explanation, that is also a defect.

## Power and clocks

Board performance depends heavily on the power profile, so a number without a
profile is not a number. Jetson profiles are named in `nvpmodel`. FPGA clocks
depend on a design that has been synthesised, so a clock in this book is either
taken from a published design or labelled as an assumption with its sensitivity
shown.
