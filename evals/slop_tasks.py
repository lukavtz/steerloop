"""SlopCodeBench-lite: three CLI tasks, three rounds each.

Design follows arXiv:2603.24755 — the agent repeatedly extends its own
solution as the specification grows, and we measure what the extensions do
to the code: size, duplication, and how much complexity piles into one
function. Checks are executed after every round, earlier rounds included.
"""

SAMPLE_WORDS = "hello world\nthe world of code\nhello again\n"


def _text(expected):
    return lambda rc, out: rc == 0 and out.strip() == expected


def _json(expected):
    import json

    def test(rc, out):
        if rc != 0:
            return False
        try:
            return json.loads(out) == expected
        except Exception:  # noqa: BLE001
            return False

    return test


def _fails(rc, out):
    return rc == 2


TASKS = [
    {
        "id": "words",
        "entry": "words.mjs",
        "fixture": {"sample.txt": SAMPLE_WORDS},
        "rounds": [
            {
                "spec": """# words

`words.mjs FILE` prints one JSON object:

    {"lines": N, "words": N, "chars": N}

lines = number of lines in the file, words = whitespace-separated tokens,
chars = characters excluding newlines. Exit 1 with a message on stderr when
the file is missing.
""",
                "checks": [("summary", ["sample.txt"], _json({"lines": 3, "words": 8, "chars": 39}))],
            },
            {
                "spec": """## Round 2

Add `--top N`. With it, print a JSON array of the N most frequent words,
most frequent first, ties alphabetical ascending. Matching is case-insensitive.

    [{"word": "hello", "count": 2}, {"word": "world", "count": 2}]
""",
                "checks": [
                    ("top2", ["sample.txt", "--top", "2"], _json([{"word": "hello", "count": 2}, {"word": "world", "count": 2}])),
                ],
            },
            {
                "spec": """## Round 3

Add `--text`. With it, print three lines instead of JSON:

    lines: 3
    words: 8
    chars: 39

An unknown flag exits 2.
""",
                "checks": [
                    ("text", ["sample.txt", "--text"], _text("lines: 3\nwords: 8\nchars: 39")),
                    ("unknown", ["sample.txt", "--nope"], _fails),
                ],
            },
        ],
    },
    {
        "id": "calc",
        "entry": "calc.mjs",
        "fixture": {},
        "rounds": [
            {
                "spec": """# calc

`calc.mjs EXPR` evaluates integer arithmetic with `+ - * /` and normal
precedence, and prints the integer result. Division truncates.
""",
                "checks": [("precedence", ["2+3*4"], _text("14")), ("div", ["9/2"], _text("4"))],
            },
            {
                "spec": """## Round 2

Support parentheses and a unary minus.
""",
                "checks": [("minus", ["-(2+3)*4"], _text("-20")), ("paren", ["2*(3+4)"], _text("14"))],
            },
            {
                "spec": """## Round 3

Support variables: `--var NAME=VALUE` may repeat. An undefined variable or a
malformed expression exits 2.
""",
                "checks": [("vars", ["--var", "x=5", "x*2+1"], _text("11")), ("bad", ["1+"], _fails)],
            },
        ],
    },
    {
        "id": "intervals",
        "entry": "intervals.mjs",
        "fixture": {},
        "rounds": [
            {
                "spec": """# intervals

`intervals.mjs A-B` prints the length in minutes of the interval A-B, where
A and B are `HH:MM` on the same day.
""",
                "checks": [("single", ["10:00-11:30"], _text("90"))],
            },
            {
                "spec": """## Round 2

Accept several intervals. Overlapping or touching intervals merge. Print the
total number of covered minutes.
""",
                "checks": [("merged", ["10:00-11:30", "11:00-12:00"], _text("120"))],
            },
            {
                "spec": """## Round 3

Add `--json`: print the merged intervals as
`[{"start": "10:00", "end": "12:00"}]` instead of the total.
""",
                "checks": [("json", ["--json", "10:00-11:30", "11:00-12:00"], _json([{"start": "10:00", "end": "12:00"}]))],
            },
        ],
    },
]
