"""Caption chunks for Episode 1, in the reference house style (docs/STYLE_GUIDE.md section 3).

Each line is one on-screen chunk (2-4 words, natural phrase breaks). *word* marks the single red
keyword. Lines starting with > are a direct quote (Playfair Display Italic, sentence case).
Chunks are aligned to the Whisper word timings in transcript.json by consuming words in order.
"""
import json
import re

CHUNKS = """
Meet *Charles* Vallow,
62 years old,
a big friendly *bear*
of a man
in suburban *Arizona*,
the kind who
fills a room
with his *personality*,
works *hard*,
provides and *adores*
his *family*.
He has a *wife*
he loves
named *Lori*
and two *kids*
at home,
a teenage *daughter*,
*Tylee*,
and a little *boy*,
*J.J.*,
seven years old,
*autistic*,
the *light*
of Charles' life.
From the *outside*,
they are an
*ordinary* American
family,
except Charles Vallow
is *terrified*
of his own *wife*,
because something
has *happened*
to Lori,
not slowly,
but *fast*.
The woman he *married*
has started
saying things,
and I want you
to really *hear* them,
because they are
that *strange*.
She tells him
she is a *god*,
that she is,
in her own words,
a *translated* being
who cannot
taste *death*
sent here to lead
a *chosen*
144,000 people
into the end
of the *world*.
She says the world
is *ending* soon.
On a *schedule*
the summer of *2020*,
she says she has
a *mission*
and a *power*
and an *angel*
standing beside her,
and then she starts
saying the *strangest*
thing of all.
She tells Charles
that he is
not *Charles* anymore,
that the *real* man
she married
is *gone*,
that something *dark*
has climbed
inside his body
and is only
wearing his *face*.
She stops using
his *name*,
she starts calling him
someone *else*.
There's a *man*
tangled up
in all of it,
someone she's met,
a *writer*
from out of state
who talks about
*visions*
and the end
of the world
and who has
told Lori
she is far more
*important*
than she ever knew.
Charles is
*frightened*,
so he does
what a frightened
person does.
He calls the *police*
to check on
his own wife,
he files for *divorce*,
and in the
court papers
he writes down,
in plain black *ink*,
the *exact* words
she said to him.
>I will kill you,
>because you're not Charles,
>and nobody will care.
Think about *that*.
A grown man
telling the *police*,
telling the *courts*,
that his wife
means to end
his *life*.
And here's the thing
about a man
like Charles,
*big*,
*capable*,
always *fine*.
Nobody takes him
*seriously*
and nobody
comes to *help*.
"""


def _norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def build_captions(path="transcript.json"):
    words = [(w["w"].strip(), w["s"], w["e"]) for seg in json.load(open(path)) for w in seg["words"]]
    # Whisper splits a couple of tokens ("J" ".J.,", "144" ",000"): merge anything with no letters/digits
    # of its own onto the previous word, and join tokens that the chunk text writes as one
    stream = "".join(_norm(w) for w, _, _ in words)
    pos, i, out = 0, 0, []
    for line in [l for l in CHUNKS.strip().splitlines() if l.strip()]:
        quote = line.startswith(">")
        text = line.lstrip(">")
        target = _norm(text.replace("*", ""))
        got, first = "", None
        while len(got) < len(target):
            w, s, e = words[i]
            if first is None and _norm(w):
                first = s
            got += _norm(w)
            last_end = e
            i += 1
        assert got == target, (line, got, target)
        out.append(dict(text=text, quote=quote, s=first, e=last_end))
    assert i == len(words), (i, len(words))
    # each chunk holds until the next one starts; across a real pause it clears 0.5s after its last word
    for a, b in zip(out, out[1:]):
        a["end"] = b["s"] if b["s"] - a["e"] < 0.7 else a["e"] + 0.5
    out[-1]["end"] = out[-1]["e"] + 0.5
    return out


if __name__ == "__main__":
    for c in build_captions():
        print(f'{c["s"]:7.2f} {c["end"]:7.2f}  {"Q " if c["quote"] else "  "}{c["text"]}')
