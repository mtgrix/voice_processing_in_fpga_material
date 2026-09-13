-- tikz_figures.lua -- turn a hand-written TikZ block into a numbered LaTeX float.
--
-- The authoring shape is a fenced div, because a caption has to be able to say
-- "*not* a vendor figure" and an attribute string cannot:
--
--     ::: {#fig-ridge .figure}
--     ```tikz
--     \begin{tikzpicture}[x=2.7cm]
--     \draw (0,0) -- (1,1);
--     \end{tikzpicture}
--     ```
--     The ridge points of both sides, on one pair of axes.
--     :::
--
-- Everything after the fence becomes the caption, and Pandoc's own LaTeX writer
-- converts it, so emphasis, code spans and characters that need escaping in LaTeX
-- behave the way they do in the prose around them.
--
-- The fence carries a whole picture, environment included, and a complete one is passed
-- through as written rather than wrapped. Wrapping it would nest two environments, which
-- is the recursion has_own_environment below refuses to allow.
--
-- Why a filter and not a raw LaTeX block in the chapter: a `\begin{tikzpicture}`
-- written straight into the markdown would reach the PDF as itself, and the build
-- gate reads that exact string as the sign of an unrendered figure (check 6 of
-- scripts/verify_book_pdf.sh). A fence that Pandoc parses first is the difference
-- between a figure and a leak.
--
-- Why TikZ and not pgfplots: pgfplots compiles on this host, but its log axes print
-- decade ticks as superscripts, which a text-layer check reads as "105" for 10^5,
-- and the package carries a compatibility surface (\pgfplotsset{compat=...}) that a
-- reader on another TeX distribution has to get right. A log-log roofline is two
-- straight segments per machine, so the axes here are drawn in plain TikZ, whose
-- presence Issue #36 confirmed by compiling a probe.
--
-- LaTeX is written with Lua long brackets at level one, [=[ and ]=], because "\l" is
-- not a legal escape in a Lua quoted string. The whole float is one string.format
-- template rather than a chain of concatenations, because a level-zero [[ ]] closes
-- early on the "]]" that a float's placement option makes, and a misplaced level-one
-- opener fails the build with "invalid long string delimiter", which is a confusing
-- error to meet in a file that is mostly prose about figures.
--
-- Issue #36. Wired in by scripts/build_book.sh as --lua-filter.

--- True for a code fence opened as ```tikz, with or without attributes.
local function is_tikz(block)
  return block.t == 'CodeBlock' and block.classes ~= nil and block.classes:includes('tikz')
end

-- A block that already carries its own environment is passed through as written, and
-- only a bare body gets wrapped. This is not a convenience: wrapping a complete picture
-- nests two of them, and pgfcorescopes.code.tex then saves \selectfont twice. The inner
-- save sees \selectfont already bound to \pgf@selectfont, whose body is
-- "\pgf@selectfontorig\nullfont", so \pgf@selectfontorig ends up defined as itself, and
-- the first node inside that selects a font -- any font= key -- expands forever. The
-- build dies with "TeX capacity exceeded, sorry [input stack size=10000]" and blames
-- the node, which is three scopes away from the line that caused it.
local function has_own_environment(text)
  return text:find('\\begin{tikzpicture}', 1, true) ~= nil
end

--- Where to point a reader who has just been refused. Pandoc records source
--- positions for blocks read from a file but not for blocks built by another
--- filter, so the fallback is the div's own first text.
local function name_of(el)
  if el.identifier ~= nil and el.identifier ~= '' then
    return '#' .. el.identifier
  end
  local position = el.source and el.source.position
  if position then
    return 'the .figure div at line ' .. position.start.line
  end
  local first = el.content[1]
  return 'the .figure div beginning ' .. (first and first.text or ''):sub(1, 40)
end

function Div(el)
  if FORMAT ~= 'latex' then
    return nil
  end
  if not el.classes:includes('figure') then
    return nil
  end

  local pictures = {}
  local caption = {}
  for _, block in ipairs(el.content) do
    if is_tikz(block) then
      pictures[#pictures + 1] = block.text
    else
      caption[#caption + 1] = block
    end
  end

  -- A .figure div with no TikZ block inside it is not ours to rewrite. It is most
  -- likely an ![](file.pdf) figure, which Pandoc already turns into a float.
  if #pictures == 0 then
    return nil
  end
  local where = name_of(el)
  if #pictures > 1 then
    error(where .. ' holds ' .. #pictures .. ' tikz blocks; one float carries one picture')
  end
  if #caption == 0 then
    error(where .. ' holds a figure with no caption, so nothing tells a reader what it shows')
  end

  -- Trailing whitespace only: pandoc.write ends the conversion with a newline, and
  -- \caption{...} on the end of a line would put that newline inside the sentence.
  local text = pandoc.write(pandoc.Pandoc(caption), 'latex'):gsub('%s+$', '')
  local placement = el.attributes['placement'] or 'htbp'
  local label = ''
  if el.identifier ~= '' then
    label = string.format([=[
\label{%s}]=], el.identifier)
  end

  local picture = pictures[1]
  local body
  if has_own_environment(picture) then
    if picture:find('\\end{tikzpicture}', 1, true) == nil then
      error(where .. ' opens a tikzpicture and never closes it')
    end
    body = picture
  else
    body = string.format([=[\begin{tikzpicture}
%s
\end{tikzpicture}]=], picture)
  end

  local out = string.format([=[\begin{figure}[%s]
\centering
\footnotesize
%s
\caption{%s}%s
\end{figure}]=], placement, body, text, label)
  return pandoc.RawBlock('tex', out)
end
