# The Streaming Bottleneck: Why Batch=1 Stalls a GPU

> *Objective: Analyze the root architectural causes behind GPU power inefficiency, memory bandwidth saturation, and latency jitter under continuous streaming audio.*

---

## 3.1 The Mismatch Between Streaming Audio and SIMT Architecture
## 3.2 Kernel Launch Overheads, Preemption, and Tail Jitter
## 3.3 Roofline Analysis: Why Voice at Batch=1 is Memory-Bound

A roofline answers one question with two lines. The horizontal axis is arithmetic
intensity: how many operations a program performs for each byte it reads. The vertical
axis is the rate the machine can sustain. A machine follows the rising line while the
work is light on arithmetic, which means it is waiting for memory, and it follows the
flat line once the work is dense enough to keep the compute units fed. The corner
between them is the ridge point, and for this book it is always the same division: peak
operations divided by peak bandwidth. `V-07-01` is the paper that introduced the plot.

[Figure 1](#fig-ridge-point-comparison) puts the Kria KV260 and two Jetson Orin models on
one pair of axes. Read the rising lines before the corners. Each is labelled with the
bandwidth that fixes its height, the Orin's is the higher of the two, and so at any
intensity left of both corners the GPU is faster in absolute terms, and nothing here says
the FPGA saves this project anything.
The claim the figure supports is narrower and it is about corners: the FPGA reaches its
own ceiling at an intensity an order of magnitude lower, so a small, bandwidth-light
accelerator can be *used* where a large one sits idle. That is the whole argument of
this chapter, and `V-07-02`, `V-07-03` and the arithmetic label in the figure are all of
it.

Two things the figure does not say are worth naming. It does not say where the Voice
Edge Benchmark sits on the horizontal axis: that number belongs to a compiled network
and a chosen kernel, and no record in this book has it, so the workload is left off the
plot rather than guessed at. It also does not resolve which Orin the project will
measure against. Figure 1 prints its two dense corners as two separate numbers for that
reason, and the band between them is drawn as a question, not as a range.

[Figure 2](#fig-clock-sensitivity) belongs to the FPGA corner alone. It varies the one
input behind that corner which is not a datasheet figure, which is why the FPGA corner of
Figure 1 is the softest number in it.

::: {#fig-ridge-point-comparison .figure}
```tikz
% One roofline per machine, on logarithmic axes. The corners are computed here rather
% than typed, so a label cannot drift away from the division it claims to be: every
% ridge below is peak operations divided by peak bandwidth, evaluated by pgfmath from
% the same two inputs the record names.
%
% pgfmath routes the operands of a division through a TeX dimension, whose ceiling is
% about 16384, so 67000/2 fails the build with "Dimension too large" while 67/2 is
% fine. Hence every peak below is held in TOPS and every height is log10(TOPS)+3,
% which is the same point on an axis labelled in GOP/s.
\begin{tikzpicture}[
  x=2.7cm, y=1.15cm,
  declare function={X(\v)=log10(\v); Y(\t)=log10(\t)+3;},
  orin/.style={blue!55!black, thick},
  nano/.style={red!65!black, thick, densely dashed},
  fpga/.style={black, thick},
  sp/.style={loosely dotted, thick},
  dot/.style={circle, inner sep=1.1pt, fill},
  t/.style={font=\scriptsize, inner sep=2pt},
]
% Inputs. Each is the number a record carries, in the unit that record states it in.
\pgfmathsetmacro{\bwOrin}{102}                % V-02-10, GB/s; V-07-02 states it too
\pgfmathsetmacro{\bwKv}{19.2}                 % V-01-13, GB/s
\pgfmathsetmacro{\pkNxdense}{50}              % V-07-02, TOPS INT8 dense
\pgfmathsetmacro{\pkNxsparse}{100}            % V-07-02, TOPS sparse
\pgfmathsetmacro{\pkNssparse}{67}             % V-02-09, Sparse INT8 TOPS
\pgfmathsetmacro{\pkNsdense}{\pkNssparse/2}   % arithmetic on V-02-31's 2x, TOPS
\pgfmathsetmacro{\pkKvone}{1248*2*0.3/1000}   % V-01-09 slices, V-07-03 clock, TOPS
\pgfmathsetmacro{\pkKvpacked}{1248*4*0.3/1000}% the packed INT8 reading of V-07-03
\pgfmathsetmacro{\gopKvone}{\pkKvone*1000}     % V-07-03 states its peaks in GOP/s, so
\pgfmathsetmacro{\gopKvpacked}{\pkKvpacked*1000}% both labels are printed from the TOPS
% The four Orin corners and the two FPGA corners: peak divided by bandwidth.
\pgfmathsetmacro{\rdNxdense}{\pkNxdense/\bwOrin*1000}
\pgfmathsetmacro{\rdNxsparse}{\pkNxsparse/\bwOrin*1000}
\pgfmathsetmacro{\rdNsdense}{\pkNsdense/\bwOrin*1000}
\pgfmathsetmacro{\rdNssparse}{\pkNssparse/\bwOrin*1000}
\pgfmathsetmacro{\rdKvone}{\pkKvone/\bwKv*1000}
\pgfmathsetmacro{\rdKvpacked}{\pkKvpacked/\bwKv*1000}
\def\xr{3.18}   % right edge, arithmetic intensity just past 1500 OP/byte
\def\yb{1}      % bottom edge, 10 GOP/s
\def\yt{5.2}    % top edge, a little above 100000 GOP/s

% Decade grid, then the two axes.
\foreach \d in {0,1,2,3} {\draw[gray!22] (\d,\yb) -- (\d,\yt);}
\foreach \d in {2,3,4,5} {\draw[gray!22] (0,\d) -- (\xr,\d);}
\draw[<->] (0,\yb) -- (\xr,\yb);
\draw[<->] (0,\yb) -- (0,\yt);
\node[t, below] at (0,\yb) {1};
\node[t, below] at (1,\yb) {10};
\node[t, below] at (2,\yb) {100};
\node[t, below] at (3,\yb) {1000};
\node[t, left] at (0,\yb) {10};
\node[t, left] at (0,2) {100};
\node[t, left] at (0,3) {1000};
\node[t, left] at (0,4) {10000};
\node[t, left] at (0,5) {100000};
\node[below=34pt, font=\small] at (\xr/2,\yb) {arithmetic intensity, OP/byte};
\node[rotate=90, above=30pt, font=\small] at (0,3.1) {sustainable rate, GOP/s};

% The two memory roofs, each named in the ink of its own line. They go in the empty
% upper-left triangle: every compute roof starts further right than this block ends,
% and the two rising lines come within 0.3 decades of each other, so neither can be
% labelled along itself.
\node[t, anchor=north west, align=left] at (0.06,\yt-0.06) {
  \textcolor{blue!55!black}{102 GB/s: V-02-10 and V-07-02}\penalty0\\
  19.2 GB/s: V-01-13};

% The gap the undecided SKU opens, drawn under the lines so it hides none of them.
\fill[red!9] ({X(\rdNsdense)},\yb) rectangle ({X(\rdNxdense)},\yt);
\node[t, red!65!black, anchor=south] at ({(X(\rdNsdense)+X(\rdNxdense))/2},\yt+0.04)
  {which SKU? V-02-28: unresolved};

% KV260: one shallow memory roof, two compute roofs. V-07-03 carries both corners.
\draw[fpga] ({X(1)},{Y(\bwKv/1000)}) -- ({X(\rdKvone)},{Y(\pkKvone)});
\draw[sp, fpga] ({X(\rdKvone)},{Y(\pkKvone)}) -- ({X(\rdKvpacked)},{Y(\pkKvpacked)});
\draw[fpga] ({X(\rdKvone)},{Y(\pkKvone)}) -- (\xr,{Y(\pkKvone)});
\draw[sp, fpga] ({X(\rdKvpacked)},{Y(\pkKvpacked)}) -- (\xr,{Y(\pkKvpacked)});
\node[dot, label={[t]below:\pgfmathprintnumber[fixed,precision=1]{\rdKvone}}]
  at ({X(\rdKvone)},{Y(\pkKvone)}) {};
\node[dot, label={[t]above:\pgfmathprintnumber[fixed,precision=1]{\rdKvpacked}}]
  at ({X(\rdKvpacked)},{Y(\pkKvpacked)}) {};
\node[t, anchor=north east] at (\xr-0.03,{Y(\pkKvone)-0.03}) {\pgfmathprintnumber[fixed,precision=1,1000 sep={}]{\gopKvone} GOP/s};
\node[t, anchor=south east] at (\xr-0.03,{Y(\pkKvpacked)+0.03}) {\pgfmathprintnumber[fixed,precision=1,1000 sep={}]{\gopKvpacked} GOP/s};

% Orin: one shared memory roof, four compute roofs. Only the Nano Super dense line is
% arithmetic this book performs rather than a figure a record carries, so it alone is
% drawn dashed in a second ink.
\draw[orin] ({X(1)},{Y(\bwOrin/1000)}) -- ({X(\rdNxsparse)},{Y(\pkNxsparse)});
\draw[orin] ({X(\rdNxdense)},{Y(\pkNxdense)}) -- (\xr,{Y(\pkNxdense)});
\draw[sp, orin] ({X(\rdNxsparse)},{Y(\pkNxsparse)}) -- (\xr,{Y(\pkNxsparse)});
\draw[nano] ({X(\rdNsdense)},{Y(\pkNsdense)}) -- (\xr,{Y(\pkNsdense)});
\draw[sp, nano] ({X(\rdNssparse)},{Y(\pkNssparse)}) -- (\xr,{Y(\pkNssparse)});
\node[dot, orin] at ({X(\rdNxdense)},{Y(\pkNxdense)}) {};
\node[dot, orin, loosely dotted] at ({X(\rdNxsparse)},{Y(\pkNxsparse)}) {};
\node[dot, nano] at ({X(\rdNsdense)},{Y(\pkNsdense)}) {};
\node[dot, nano, loosely dotted] at ({X(\rdNssparse)},{Y(\pkNssparse)}) {};

% The four Orin ridge values are deliberately absent from the axis. They sit 0.17
% decades apart, which no rotated label clears either, and the key below already names
% each one beside the roof it belongs to.

% The key, outside the frame. Every plotted quantity is named here or on its own line.
\node[t, anchor=north west, align=left] at (\xr+0.14,\yt-0.06) {
  \textcolor{blue!55!black}{\textbf{Orin NX 16GB, MAXN}} V-07-02\penalty0\\
  \hspace*{1.5em}50 TOPS dense, corner \pgfmathprintnumber[fixed,precision=1]{\rdNxdense}\penalty0\\
  \hspace*{1.5em}100 TOPS sparse, \pgfmathprintnumber[fixed,precision=1]{\rdNxsparse}\penalty0\\
  \textcolor{red!65!black}{\textbf{Orin Nano Super}} V-02-09, V-02-10\penalty0\\
  \hspace*{1.5em}67 TOPS sparse, \pgfmathprintnumber[fixed,precision=1]{\rdNssparse}\penalty0\\
  \hspace*{1.5em}\textcolor{red!65!black}{33.5 dense, \pgfmathprintnumber[fixed,precision=1]{\rdNsdense}: no record}\penalty0\\
  \textbf{Kria KV260} V-07-03\penalty0\\
  \hspace*{1.5em}\pgfmathprintnumber[fixed,precision=1,1000 sep={}]{\gopKvone} GOP/s, corner \pgfmathprintnumber[fixed,precision=1]{\rdKvone}\penalty0\\
  \hspace*{1.5em}\pgfmathprintnumber[fixed,precision=1,1000 sep={}]{\gopKvpacked} packed, \pgfmathprintnumber[fixed,precision=1]{\rdKvpacked}\penalty0\\
  dotted: sparse or packed reading\penalty0\\
  band: the dense corners of both SKUs
};
\end{tikzpicture}
```
The ridge points of the two sides, on the axes `V-07-01` defines. A rising line is one
machine's memory bandwidth and a flat line is its compute peak, so the corner where they
meet is the arithmetic intensity at which that machine stops waiting for memory. Each
corner is printed as the division that produced it and computed at compile time from the
inputs its record names; the red dashed corner is the one quantity here that no record
carries, because it is this book's own division of a sparse TOPS figure by the 2x
sparsity factor of `V-02-31`. Dotted lines are the sparse or packed second reading of a
machine, solid lines the dense reading, and the shaded band is the gap between the two
dense SKUs while `V-02-28` stays unresolved.
:::

::: {#fig-clock-sensitivity .figure}
```tikz
% The FPGA ridge point against the clock of its DSP array, with the Orin NX dense ridge
% as a horizontal reference. Both slopes are the same division as in the figure above,
% drawn here as a line instead of a point: peak operations per MHz divided by bandwidth.
\begin{tikzpicture}[
  x=0.0055cm, y=0.017cm,
  fpga/.style={black, thick},
  packed/.style={black, thick, densely dotted},
  dot/.style={circle, inner sep=1.1pt, fill},
  orin/.style={blue!55!black, thick},
  t/.style={font=\scriptsize, inner sep=2pt},
]
% Inputs, as above: 1248 slices from V-01-09, 19.2 GB/s from V-01-13, and two or four
% operations per slice per cycle from the two readings of V-07-03. Division first, and
% only ever between small numbers, because pgfmath sends operands to a TeX dimension.
\pgfmathsetmacro{\slopenone}{1248*2/19.2/1000}   % OP/byte per MHz, one MAC per slice
\pgfmathsetmacro{\slopedense}{2*\slopenone}      % the packed INT8 reading
\pgfmathsetmacro{\pkNxdense}{50}                 % V-07-02, TOPS
\pgfmathsetmacro{\bwOrin}{102}                   % V-02-10, GB/s
\pgfmathsetmacro{\rdNxdense}{\pkNxdense/\bwOrin*1000}
\pgfmathsetmacro{\fAssume}{300}                  % the clock V-07-03's figures assume
\pgfmathsetmacro{\fAlt}{500}                     % the clock its note offers
\pgfmathsetmacro{\ridgeAssume}{\slopenone*\fAssume}
\pgfmathsetmacro{\ridgeAlt}{\slopenone*\fAlt}
\pgfmathsetmacro{\gapAssume}{\rdNxdense/\ridgeAssume}
\pgfmathsetmacro{\gapAlt}{\rdNxdense/\ridgeAlt}
\pgfmathsetmacro{\fCross}{\rdNxdense/\slopedense} % where packed meets the Orin ridge
\pgfmathsetmacro{\crossRatio}{\fCross/\fAssume}   % that clock as a multiple of the assumed one
\def\xmax{2000}
\def\ymax{540}

\draw[gray!22] (0,\rdNxdense) -- (\xmax,\rdNxdense);
\foreach \f in {500,1000,1500,2000} {\draw[gray!22] (\f,0) -- (\f,\ymax);}
\draw[<->] (0,0) -- (\xmax,0);
\draw[<->] (0,0) -- (0,\ymax);
\node[t, below] at (0,0) {0};
\node[t, below] at (500,0) {500};
\node[t, below] at (1000,0) {1000};
\node[t, below] at (1500,0) {1500};
\node[t, below] at (2000,0) {2000};
\node[t, left] at (0,100) {100};
\node[t, left] at (0,200) {200};
\node[t, left] at (0,300) {300};
\node[t, left] at (0,400) {400};
\node[t, left] at (0,500) {500};
\node[below=16pt, font=\small] at (\xmax/2,0) {DSP clock, MHz};
\node[rotate=90, above=26pt, font=\small] at (0,270) {ridge point, OP/byte};

\draw[fpga] (0,0) -- (\xmax,\slopenone*\xmax);
\draw[packed] (0,0) -- (\xmax,\slopedense*\xmax);
\draw[orin] (0,\rdNxdense) -- (\xmax,\rdNxdense);
\node[t, orin, anchor=south west] at (120,\rdNxdense+8)
  {Orin NX dense ridge, \pgfmathprintnumber[fixed,precision=1]{\rdNxdense}: V-07-02};
\node[t, anchor=north west, text width=3.9cm, align=left] at (1080,150)
  {KV260 dense ridge: V-01-09 and V-01-13, and the packed reading of V-07-03 above it};

% The two clocks, and the ratio to the Orin corner that each implies.
\foreach \c/\lab in {300/assumed, 500/alternative} {
  % One ridge per clock, computed once: printnumber takes a number, not an
  % expression, and the two coordinates want the same value.
  \pgfmathsetmacro{\ridgeAtC}{\slopenone*\c}
  \draw[gray!60] (\c,0) -- (\c,\ridgeAtC);
  \node[dot] at (\c,\ridgeAtC) {};
  \node[t, below right] at (\c,\ridgeAtC)
    {\lab: {\c} MHz gives \pgfmathprintnumber[fixed,precision=1]{\ridgeAtC}};
}
\draw[gray!60] (\fCross,0) -- (\fCross,\rdNxdense);
\node[circle, inner sep=1.3pt, draw, black] at (\fCross,\rdNxdense) {};
\node[t, anchor=south west, text width=4.6cm, align=left] at (120,350)
  {Ratio to the Orin dense ridge:\penalty0\\
  \hspace*{1.5em}\pgfmathprintnumber[fixed,precision=1]{\gapAssume}x at 300 MHz,\penalty0\\
  \hspace*{1.5em}\pgfmathprintnumber[fixed,precision=1]{\gapAlt}x at 500 MHz.};
\node[t, anchor=north west, text width=3.0cm, align=left] at (\fCross+16,\rdNxdense-10)
  {packed meets the ridge at
  \pgfmathprintnumber[fixed,precision=0,1000 sep={}]{\fCross} MHz,
  \pgfmathprintnumber[fixed,precision=1]{\crossRatio}x the assumed clock};
\end{tikzpicture}
```
How much of the ridge-point gap is the clock. `V-07-03` states its KV260 figures at 300
MHz, which is an assumption about a board this project has not measured, and its own note
says what the same inputs give at 500 MHz. Both lines here are the division plotted as a
single corner in Figure 1, so Figure 2 answers one question only: does the gap survive the
assumption. It does. The FPGA ridge stays an order of magnitude below the
Orin dense ridge across every clock this book has reason to name, and the gap closes only
at the clock tagged at the right of the plot, which comes from arithmetic rather than
from a record, and which no record says the part runs at.
:::

## 3.4 Motivation for Spatial Hardware Computing on FPGAs
