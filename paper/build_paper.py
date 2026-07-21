#!/usr/bin/env python3
"""Build the academic preprint PDF from a single self-contained Python source."""

from __future__ import annotations

import math
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, KeepTogether, NextPageTemplate, Paragraph, Spacer


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tools"))

from academic_pdf import (  # noqa: E402
    ABSTRACT,
    ACCENT,
    AUTHOR,
    BODY,
    BODY_SMALL,
    CAPTION,
    DATE,
    HAIRLINE,
    H2,
    INK,
    LIGHT,
    MUTED,
    PROOF,
    REFERENCE,
    SANS,
    SANS_BOLD,
    SERIF,
    SERIF_BOLD,
    SERIF_ITALIC,
    SUBTITLE,
    TITLE,
    Rule,
    booktabs,
    bullet,
    code_block,
    equation,
    h1,
    h2,
    make_document,
    p,
    proof_start,
    theorem,
)


OUTPUT = Path(__file__).resolve().with_name("grand-coupling-counterexample.pdf")
TITLE_TEXT = "Coalescence-Class Cardinalities in Finite Grand Couplings Need Not Be Deterministic"
SHORT_TITLE = "Coalescence-class cardinalities"
AUTHOR_TEXT = "Luke Kabbash | Project initiator"
MANUSCRIPT_DATE = "20 July 2026"


class ConstructionFigure(Flowable):
    """Two-panel vector diagram of the six-state construction."""

    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 166

    def wrap(self, avail_width, avail_height):
        return min(self.width, avail_width), self.height

    @staticmethod
    def _arrow(canvas, x1, y1, x2, y2, *, color=INK, width=0.8):
        canvas.setStrokeColor(color)
        canvas.setFillColor(color)
        canvas.setLineWidth(width)
        canvas.line(x1, y1, x2, y2)
        angle = math.atan2(y2 - y1, x2 - x1)
        size = 4.2
        left = angle + 2.55
        right = angle - 2.55
        path = canvas.beginPath()
        path.moveTo(x2, y2)
        path.lineTo(x2 + size * math.cos(left), y2 + size * math.sin(left))
        path.lineTo(x2 + size * math.cos(right), y2 + size * math.sin(right))
        path.close()
        canvas.drawPath(path, fill=1, stroke=0)

    @staticmethod
    def _node(canvas, x, y, label, *, filled=False, radius=11):
        canvas.setFillColor(LIGHT if filled else colors.white)
        canvas.setStrokeColor(ACCENT if filled else INK)
        canvas.setLineWidth(0.85)
        canvas.circle(x, y, radius, fill=1, stroke=1)
        canvas.setFillColor(INK)
        canvas.setFont(SANS, 7.1)
        canvas.drawCentredString(x, y - 2.5, label)

    def draw(self):
        c = self.canv
        split = 222
        c.setStrokeColor(HAIRLINE)
        c.setLineWidth(0.4)
        c.line(split + 8, 5, split + 8, 161)

        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 9.3)
        c.drawString(0, 158, "(a) Auxiliary graph and the fibers of A")
        xs = (42, 109, 176)
        for y in (114, 76):
            c.setStrokeColor(INK)
            c.setLineWidth(0.65)
            c.line(xs[0] + 11, y, xs[1] - 11, y)
            c.line(xs[1] + 11, y, xs[2] - 11, y)
        for side, y in (("L", 114), ("R", 76)):
            for index, x in enumerate(xs):
                self._node(c, x, y, f"{side}{index}", filled=index % 2 == 0)

        c.setFont(SERIF, 7.8)
        c.setFillColor(INK)
        c.drawString(10, 43, "shaded: A^-1(L0) = {L0, L2, R0, R2}")
        c.drawString(10, 31, "open:    A^-1(L1) = {L1, R1}")
        c.setFont(SERIF_ITALIC, 7.4)
        c.setFillColor(MUTED)
        c.drawString(10, 13, "G is the disjoint union of two three-vertex paths.")

        x0 = split + 28
        panel_width = self.width - x0
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 9.3)
        c.drawString(x0, 158, "(b) Functional graph of C")
        labels = ("L0", "R0", "L1", "R1", "L2", "R2")
        step = (panel_width - 30) / 5
        node_x = [x0 + 15 + step * index for index in range(6)]
        node_y = 91
        for index in range(5):
            self._arrow(c, node_x[index] + 10.5, node_y, node_x[index + 1] - 10.5, node_y)
        for x, label in zip(node_x, labels, strict=True):
            self._node(c, x, node_y, label, radius=10.5)

        c.setStrokeColor(ACCENT)
        c.setFillColor(ACCENT)
        c.setLineWidth(0.8)
        path = c.beginPath()
        path.moveTo(node_x[5], node_y + 10.5)
        path.curveTo(node_x[5], 137, node_x[2], 137, node_x[2], node_y + 10.5)
        c.drawPath(path, fill=0, stroke=1)
        angle = -math.pi / 2
        size = 4.2
        tip_x, tip_y = node_x[2], node_y + 10.5
        arrow = c.beginPath()
        arrow.moveTo(tip_x, tip_y)
        arrow.lineTo(tip_x + size * math.cos(angle + 2.55), tip_y + size * math.sin(angle + 2.55))
        arrow.lineTo(tip_x + size * math.cos(angle - 2.55), tip_y + size * math.sin(angle - 2.55))
        arrow.close()
        c.drawPath(arrow, fill=1, stroke=0)

        c.setFillColor(INK)
        c.setFont(SERIF, 7.8)
        c.drawString(x0 + 12, 53, "L0 → R0 → L1 → R1 → L2 → R2")
        c.drawString(x0 + 12, 39, "and R2 → L1")
        c.setFillColor(MUTED)
        c.setFont(SERIF_ITALIC, 7.4)
        c.drawString(x0 + 12, 13, "Both A and C preserve every edge of G.")


class ParityLawFigure(Flowable):
    """Chronology and exact law without decorative chart furniture."""

    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 154

    def wrap(self, avail_width, avail_height):
        return min(self.width, avail_width), self.height

    def draw(self):
        c = self.canv
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 9.4)
        c.drawString(0, 143, "Initial run and terminal profile")

        start_x = 23
        end_x = 229
        y = 108
        c.setStrokeColor(INK)
        c.setLineWidth(0.6)
        c.line(start_x, y, end_x, y)
        for index, x in enumerate((36, 73, 110, 147)):
            c.setFillColor(colors.white)
            c.setStrokeColor(INK)
            c.circle(x, y, 9, fill=1, stroke=1)
            c.setFillColor(INK)
            c.setFont(SANS_BOLD, 7.5)
            c.drawCentredString(x, y - 2.6, "C")
        c.setFillColor(MUTED)
        c.setFont(SERIF_ITALIC, 8)
        c.drawCentredString(175, y - 2, "···")
        c.setFillColor(LIGHT)
        c.setStrokeColor(ACCENT)
        c.circle(216, y, 10, fill=1, stroke=1)
        c.setFillColor(INK)
        c.setFont(SANS_BOLD, 7.7)
        c.drawCentredString(216, y - 2.6, "A")
        c.setFont(SERIF, 8)
        c.drawString(22, 83, "T initial copies of C; then Q = A C^T")

        divider = 248
        c.setStrokeColor(HAIRLINE)
        c.line(divider, 23, divider, 135)
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 8.7)
        c.drawString(divider + 18, 120, "T even")
        c.drawString(divider + 18, 67, "T odd")
        c.setFont(SERIF, 9.1)
        c.drawString(divider + 78, 120, "profile (2m, 2m+2)")
        c.drawString(divider + 78, 67, "profile (2m+1, 2m+1)")
        c.setFont(SERIF_ITALIC, 8.5)
        c.setFillColor(ACCENT)
        c.drawString(divider + 78, 101, "sum p(1-p)^(2k) = 1/(2-p)")
        c.drawString(divider + 78, 48, "sum p(1-p)^(2k+1) = (1-p)/(2-p)")
        c.setFillColor(MUTED)
        c.setFont(SERIF_ITALIC, 7.8)
        c.drawString(0, 10, "The first A occurs almost surely; its parity history selects the permanent kernel.")


def figure_caption(number: int, text: str) -> Paragraph:
    return p(f"<b>Figure {number}.</b> {text}", CAPTION)


def reference(number: int, text: str) -> Paragraph:
    return p(f"[{number}] {text}", REFERENCE)


def build_story(width: float):
    story = [
        Spacer(1, 6),
        p(TITLE_TEXT, TITLE),
        p("An explicit family and a computer-assisted state-minimality theorem", SUBTITLE),
        p(AUTHOR_TEXT, AUTHOR),
        p(MANUSCRIPT_DATE, DATE),
        Rule(color=INK, thickness=0.75, space_after=10),
        p("<b>Abstract.</b>", H2),
        p(
            "Let F<sub>1</sub>, F<sub>2</sub>, ... be independent random self-maps of a finite set, and apply each map simultaneously to trajectories started from every state. Grimmett and Holmes asked whether, for a fixed consistent grand coupling, the cardinalities of the eventual coalescence classes must be deterministic. We answer in the negative. For every m ≥ 1 and 0 &lt; p &lt; 1, we construct a two-map coupling on 4m+2 states whose terminal profile is (2m, 2m+2) with probability 1/(2-p) and (2m+1, 2m+1) with probability (1-p)/(2-p). The induced Markov chain is irreducible and aperiodic, and exactly two classes remain almost surely. The proof is symbolic. A separate exhaustive kernel-graph census establishes, with computer assistance, that no example exists on fewer than six states; thus the six-state instance is state-minimal without a restriction on support size. Reproducible Python and C++ implementations accompany the manuscript.",
            ABSTRACT,
        ),
        p(
            "<b>Keywords.</b> grand coupling; random mapping representation; coalescence; transformation monoid; kernel graph; synchronizing automaton; computer-assisted proof",
            BODY_SMALL,
        ),
        p(
            "<b>Mathematics Subject Classification (2020).</b> Primary 60J10; secondary 20M20, 05C15, 68Q45.",
            BODY_SMALL,
        ),
        NextPageTemplate("body"),
    ]

    story.extend(
        [
            h1("1. Introduction"),
            p(
                "A random mapping representation writes a finite Markov chain as repeated application of random self-maps. When one map is applied to every initial state at each time, the resulting process is a grand coupling: trajectories that meet remain together. This representation is classical in the study of iterated random functions [2], synchronization, and exact sampling [9].",
            ),
            p(
                "Grimmett and Holmes [1, Open Problem 3.11] ask whether the multiset of cardinalities of the forward coalescence classes is deterministic. Their number is almost surely constant, but the classes themselves may be random. Their four-state example randomizes the paired labels while leaving the size profile equal to (2,2) in every outcome. The question is whether the sizes can also vary under one fixed transition matrix and one fixed map law.",
            ),
            p(
                "They can. The counterexample below uses two maps on six states and extends to a family on every state count 4m+2. Its mechanism is elementary: one map collapses two odd paths according to vertex parity, while a second map changes the relative parity of the paths. The first occurrence of the collapsing map fixes a rank-two kernel forever. The parity of the preceding run chooses between an unequal and an equal pair of block sizes.",
            ),
            p(
                "The construction lies at the intersection of finite random dynamical systems and transformation semigroups. Minimum-rank maps form the minimal ideal of a finite transformation monoid [3]. Kernel graphs connect non-synchronizing monoids with graph colorings and endomorphisms [4-6], while the integer partition of kernel-block sizes is already known as kernel type [7]. The contribution claimed here is narrower: an explicit negative answer to the probability question in [1], its exact infinite family and terminal law, and a computer-assisted state-minimality result.",
            ),
            p(
                "A targeted search of exact phrases, the source title and DOI, arXiv, publisher records, and author publication pages through 20 July 2026 found no public resolution of Open Problem 3.11. A negative search is not proof of priority. The complete reproduction pipeline passes, but the manuscript has not received independent peer review.",
                BODY_SMALL,
            ),
        ]
    )

    story.extend(
        [
            h1("2. Setting and notation"),
            p(
                "Let S be finite, let Map(S)=S<super>S</super> be the set of self-maps of S, and let μ be a probability measure on Map(S). Let F<sub>1</sub>, F<sub>2</sub>, ... be i.i.d. with law μ. Products are forward products",
            ),
            equation("Q<sub>t</sub> = F<sub>t</sub> F<sub>t-1</sub> ··· F<sub>1</sub>, &nbsp;&nbsp; where &nbsp; (fg)(x)=f(g(x))."),
            p(
                "The law μ is consistent with a transition matrix P when",
            ),
            equation("P(x,y) = μ{f ∈ Map(S) : f(x)=y}."),
            p(
                "Two states x and y coalesce if Q<sub>t</sub>(x)=Q<sub>t</sub>(y) for some t. The common maps then keep them together. For a map f, write ker(f) for its partition into fibers and rank(f)=|f(S)|. The <i>profile</i> of f is the sorted vector of its fiber cardinalities. The terminal profile is the profile of the eventual coalescence partition.",
            ),
            theorem(
                "Lemma 1 (kernel monotonicity).",
                [
                    "For self-maps f and q, ker(q) refines ker(fq). Consequently, a forward product can merge kernel blocks but cannot split them. If rank(q) is already the minimum rank of the support-generated monoid, then every later product has the same kernel as q.",
                ],
            ),
            proof_start(
                "If q(x)=q(y), then f(q(x))=f(q(y)). Thus every block of ker(q) lies in a block of ker(fq). At minimum rank, a strict merger would decrease the number of blocks and contradict minimality."
            ),
        ]
    )

    story.extend(
        [
            h1("3. The counterexample family"),
            h2("3.1 Construction"),
            p(
                "Fix m ≥ 1 and set d=2m+1. Take two disjoint paths",
            ),
            equation("L<sub>0</sub>-L<sub>1</sub>-···-L<sub>2m</sub> &nbsp;&nbsp; and &nbsp;&nbsp; R<sub>0</sub>-R<sub>1</sub>-···-R<sub>2m</sub>."),
            p(
                "Their 4m+2 vertices form S<sub>m</sub>. Define A and C by",
            ),
            equation("A(L<sub>i</sub>)=A(R<sub>i</sub>)=L<sub>i mod 2</sub>,"),
            equation(
                "C(L<sub>i</sub>)=R<sub>i</sub>, &nbsp; C(R<sub>i</sub>)=L<sub>i+1</sub> for i&lt;2m, &nbsp; and &nbsp; C(R<sub>2m</sub>)=L<sub>2m-1</sub>."
            ),
            p(
                "Let μ=pδ<sub>A</sub>+(1-p)δ<sub>C</sub>, where 0 &lt; p &lt; 1, and let P be the consistent transition matrix induced by μ.",
            ),
            theorem(
                "Theorem 1 (counterexample family).",
                [
                    "For every integer m ≥ 1 and p ∈ (0,1), the pair (P,μ) above is a consistent grand coupling of an irreducible, aperiodic Markov chain on 4m+2 states. Its forward coalescence partition has two blocks almost surely. Its sorted block-size vector is",
                    "(2m, 2m+2) with probability 1/(2-p), and (2m+1, 2m+1) with probability (1-p)/(2-p).",
                    "Both outcomes therefore have positive probability under the same P and μ.",
                ],
            ),
            h2("3.2 Proof of Theorem 1"),
            proof_start(
                "Consistency is immediate from P(x,y)=p 1{A(x)=y}+(1-p) 1{C(x)=y}. The C-orbit of L0 visits every vertex before entering the final four-cycle. From any vertex, C reaches an even-indexed vertex in that cycle, and A sends it to L0. Thus the positive-transition digraph is strongly connected."
            ),
            p(
                "Since A(L0)=L0 with positive probability, the irreducible chain has a self-loop and is aperiodic.",
                PROOF,
            ),
            p(
                "Both A and C are endomorphisms of the loopless graph formed by the two paths. For A this is the parity coloring of a bipartite graph. For C, an edge L<sub>i</sub>L<sub>i+1</sub> maps to R<sub>i</sub>R<sub>i+1</sub>; an edge R<sub>i</sub>R<sub>i+1</sub> maps to L<sub>i+1</sub>L<sub>i+2</sub>, except at the endpoint, where it maps to L<sub>2m</sub>L<sub>2m-1</sub>. Every supported word is therefore a graph endomorphism. A constant map would send an edge to a loop, so every supported word has rank at least two.",
                PROOF,
            ),
            p(
                "The first A occurs almost surely. If T copies of C precede it, the prefix product is A C<super>T</super>, whose rank is at most two and hence exactly two. All later prefixes are still graph endomorphisms, so their rank cannot fall below two. Lemma 1 then makes the rank-two kernel permanent.",
                PROOF,
            ),
            p(
                "It remains to count its fibers. The map C<super>2</super> stays on the same path and reverses index parity at every vertex, including the reflected endpoint. Hence an even power of C changes parity in the same way on both paths. Applying A then gives the original parity counts: each path contains m+1 even and m odd indices, so the sorted profile is (2m,2m+2). An odd power of C puts the two paths in opposite parity phases before A. Each fiber then receives m vertices from one path and m+1 from the other, giving (2m+1,2m+1).",
                PROOF,
            ),
            p(
                "Finally, Pr(T=t)=p(1-p)<super>t</super>. Summing the even and odd terms gives",
                PROOF,
            ),
            equation("Pr(T even) = p Σ<sub>k≥0</sub>(1-p)<super>2k</super> = 1/(2-p),"),
            equation("Pr(T odd) = p Σ<sub>k≥0</sub>(1-p)<super>2k+1</super> = (1-p)/(2-p)."),
            p(
                "This proves the theorem.",
                PROOF,
            ),
            KeepTogether(
                [
                    ConstructionFigure(width),
                    figure_caption(
                        1,
                        "The six-state instance m=1. Panel (a) shows the auxiliary graph and the two fibers of A. Panel (b) shows the directed functional graph of C. The undirected path edges in (a) are proof devices, not Markov transitions. Both maps preserve those edges; because the graph is loopless, no supported word can be constant.",
                    ),
                ]
            ),
            KeepTogether(
                [
                    ParityLawFigure(width),
                    figure_caption(
                        2,
                        "The exact terminal law. Composition is read chronologically from left to right in the displayed draws and algebraically as A C<super>T</super>. Simulation is unnecessary: the two probabilities are geometric sums.",
                    ),
                ]
            ),
        ]
    )

    story.extend(
        [
            h1("4. The six-state instance"),
            p(
                "For m=1, identify (L0,L1,L2,R0,R1,R2) with (0,1,2,3,4,5). The maps are",
            ),
            equation("A=(0,1,0,0,1,0), &nbsp;&nbsp; C=(3,4,5,1,2,1)."),
            booktabs(
                [
                    ("state", "L0", "L1", "L2", "R0", "R1", "R2"),
                    ("A", "L0", "L1", "L0", "L0", "L1", "L0"),
                    ("C", "R0", "R1", "R2", "L1", "L2", "L1"),
                ],
                [0.56 * inch] + [0.99 * inch] * 6,
                font_size=7.8,
            ),
            Spacer(1, 5),
            p(
                "If the first draw is A, the terminal blocks are {L0,L2,R0,R2} and {L1,R1}, with profile (2,4). If the first two draws are C,A, the terminal blocks are {L0,L2,R1} and {L1,R0,R2}, with profile (3,3). These cylinder events have probabilities p and (1-p)p. For p=1/2, the complete terminal law is (2,4) with probability 2/3 and (3,3) with probability 1/3.",
            ),
            p(
                "Exact closure supplies a compact cross-check. The support-generated semigroup has 21 nonidentity elements; the prefix-product chain has 22 reachable states when the identity is included; its minimum rank is two; and every rank-two kernel is permanent. These computations corroborate the proof but are not used by it.",
            ),
        ]
    )

    story.extend(
        [
            h1("5. State minimality"),
            theorem(
                "Theorem 2 (computer-assisted state minimality).",
                [
                    "No irreducible grand coupling on at most five states has a nonconstant terminal block-size profile. Consequently, the six-state construction is state-minimal, with no restriction on the number of maps in the support.",
                ],
            ),
            h2("5.1 Reduction to a finite graph census"),
            p(
                "Let M be the transformation monoid generated by the support of μ, and let r be its minimum rank. Since every support word has positive probability, a fixed minimum-rank word appears almost surely in disjoint i.i.d. blocks. At that occurrence the forward prefix reaches rank r, and Lemma 1 fixes its kernel thereafter. Irreducibility of P is equivalent to transitivity of the action of M on S.",
            ),
            p(
                "Define the kernel graph Gr(M) on S by joining distinct x and y exactly when no element of M collapses them. Every element of M is an endomorphism of Gr(M). If f has rank r, then f(S) is an r-clique: otherwise a later map could collapse two image points and produce rank below r. The fibers of f form a proper r-coloring. It follows that",
            ),
            equation("ω(Gr(M)) = χ(Gr(M)) = r."),
            p(
                "If terminal profiles vary, this graph has at least two optimal coloring-size profiles. It also has no isolated vertex. Indeed, r≥2 gives an edge; if v were isolated, transitivity would map one endpoint of an edge to v, while endomorphism preservation would require an edge incident with v. Finally, End(Gr(M)) is transitive because it contains M. Thus any smaller counterexample would yield a simple graph with all four properties: no isolates, equal clique and chromatic numbers, multiple optimal color profiles, and a transitive endomorphism monoid.",
            ),
            h2("5.2 Exhaustive result"),
            p(
                "The supplied census enumerates every labelled simple graph on n≤5 vertices, all set partitions needed for exact chromatic profiles, all vertex subsets needed for the clique number, and all n<super>n</super> endofunctions needed for the endomorphism monoid. A separately structured implementation recomputes colorings by surjective color assignments, canonicalizes graphs under every relabelling, and independently tests endomorphism transitivity.",
            ),
            booktabs(
                [
                    ("order", "graphs after coloring filter", "isomorphism types", "transitive End(G)"),
                    ("1-4", "0", "0", "0"),
                    ("5", "150 labelled", "3", "0"),
                    ("6, rank 2", "90 labelled", "1", "1"),
                ],
                [0.92 * inch, 2.2 * inch, 1.55 * inch, 1.52 * inch],
                font_size=8.0,
            ),
            Spacer(1, 5),
            p(
                "At order five, all three surviving isomorphism types have optimal profiles (1,1,3) and (1,2,2), with 48, 42, and 50 endomorphisms respectively; none acts transitively. At order six and rank two, the unique surviving isomorphism type is the disjoint union of two three-vertex paths. It has 144 endomorphisms, a transitive endomorphism monoid, and profiles (2,4) and (3,3). Only the n≤5 census is needed for the lower bound; the n=6 line is a consistency check against the construction.",
            ),
            p(
                "The theorem is computer-assisted because its last step depends on exhaustive finite enumeration. The mathematical reduction is independent of the program. A redundant C++ search over all unordered two-map supports on four and five states also finds no example, but that narrower search is not the basis for the all-support statement.",
            ),
        ]
    )

    story.extend(
        [
            h1("6. Computational verification and reproducibility"),
            p(
                "The release separates theorem-bearing checks from exploration. All mathematical verifiers use only the Python standard library or C++20. The document builders are separate and require ReportLab and pypdf. From the repository root, the full verification is",
            ),
            code_block(["./reproduce.sh --trials 100000"], width),
            p(
                "The script first checks every file against MANIFEST.sha256. It then runs independent exact Python and C++ checks of the six-state example, exact family closure, two independently organized graph censuses, the exhaustive two-map searches for n=4 and n=5, sanitizer builds, deterministic property sweeps, exact rational stationarity checks, and seeded Monte Carlo smoke tests. A temporary build directory is removed on exit.",
            ),
            booktabs(
                [
                    ("claim", "decisive basis", "status"),
                    ("nonconstant terminal profile", "explicit construction and symbolic proof", "proved"),
                    ("exact two-atom law", "geometric series", "proved"),
                    ("six states are minimal", "graph reduction and exhaustive census", "computer-assisted"),
                    ("implementation agrees", "independent Python/C++, sanitizers, properties", "verified"),
                    ("publication priority", "targeted public search only", "not established"),
                ],
                [1.45 * inch, 3.25 * inch, 1.5 * inch],
                font_size=7.85,
            ),
            Spacer(1, 6),
            p(
                "The exact six-state programs report 22 reachable prefix states including the identity, 21 nonidentity semigroup elements, minimum rank two, and precisely the profiles (2,4) and (3,3). The family is closed exactly in Python for m=1,...,8 and independently in C++ for m=1,...,24, reaching 98 states. The observed monoid size 20m+2 is asserted over that tested range but is not claimed here as a theorem for all m.",
            ),
            p(
                "The exhaustive two-map program freezes its complete counts: 32,640 pairs, 10,476 strongly connected pairs, and 1,152 nonsynchronizing pairs at n=4; 4,881,250, 1,277,160, and 60,000 respectively at n=5. A changed count makes the program fail rather than merely print a different result.",
            ),
            p(
                "Monte Carlo is deliberately subordinate. Its fixed-seed trials compare empirical frequencies with the exact law and fail only as a statistical smoke test. No simulation, floating-point calculation, or large search is needed to establish Theorem 1.",
            ),
        ]
    )

    story.extend(
        [
            h1("7. Consequences and research directions"),
            h2("7.1 What rank omits"),
            p(
                "Synchronization records whether rank one is attainable; minimum-rank theory records how many images survive. This example shows that rank does not determine how the original states are distributed among the surviving fibers. The natural additional statistic is the hitting distribution of kernel types when the random prefix product first enters the minimum-rank ideal. In the present family this terminal kernel-type law has two atoms and is explicit.",
            ),
            p(
                "The distinction concerns cardinality, not stationary block mass. In the transitive setting, Steinberg [3, Theorem 10.4] gives stationary mass 1/r to every block of a minimum-rank kernel. Thus both blocks in the six-state example have stationary mass 1/2 under either profile, even though a uniformly chosen initial label sees different block sizes.",
            ),
            h2("7.2 A concrete computational problem"),
            p(
                "For a finite support, one can construct the reachable prefix-product chain, identify its minimum-rank states, label those states by kernel type, and solve an absorbing Markov-chain system for the exact hitting probabilities. The result is a coupling profiler that reports more than coalescence number: terminal profile law, time to minimum rank, largest-block distribution, and collision or imbalance costs. This is immediately implementable for small transformation supports; scalable quotienting and complexity bounds remain research problems.",
            ),
            h2("7.3 Coupling design"),
            p(
                "A transition matrix generally admits many random mapping representations. Their weights satisfy linear marginal constraints, but the induced semigroup and its terminal kernels depend combinatorially on which maps receive positive mass. This suggests an optimization problem: among couplings consistent with a fixed P, minimize time to a target rank, constrain the terminal profile law, or optimize a balance objective. Mixed-integer programming, SAT or SMT search, and column generation over maps are plausible proposal engines; exact closure and rational arithmetic can then certify a candidate. No complexity or performance advantage is established here.",
            ),
            h2("7.4 Limits of immediate application"),
            p(
                "The construction is a sharp test case for systems driven by common random instructions, including finite automata and replicated-state simulations. It shows that identical marginal dynamics and a fixed number of surviving groups do not force fixed group cardinalities. It does not, by itself, improve coupling from the past, distributed load balancing, or any production protocol. Forward and backward products must be distinguished carefully [1,9].",
            ),
            h2("7.5 Open problems"),
            bullet("Characterize the sets of kernel types that can occur at minimum rank in a transitive transformation monoid."),
            bullet("For fixed n and minimum rank r, maximize the number or entropy of attainable terminal profiles."),
            bullet("Characterize transition matrices P for which every consistent grand coupling has a deterministic terminal profile."),
            bullet("Optimize the terminal kernel-type law over random mapping representations of a fixed P."),
            bullet("Find a structural, non-computational proof of the obstruction on at most five states."),
            bullet("Prove or refute the observed monoid-size formula |M<sub>m</sub><super>1</super>|=20m+2 for the family."),
            bullet("Determine which forward profile statements have valid backward or coupling-from-the-past analogues."),
        ]
    )

    story.extend(
        [
            h1("Appendix A. Census method"),
            p(
                "For each n≤5, enumerate the 2<super>n(n-1)/2</super> labelled simple graphs. Discard graphs with isolated vertices. Enumerate all set partitions of the vertex set, retain the proper colorings with the fewest blocks, and record their sorted block-size profiles. Enumerate all vertex subsets to compute the clique number. Retain only graphs with ω=χ and at least two optimal profiles. Finally, enumerate all n<super>n</super> self-maps, retain exactly the graph endomorphisms, and test reachability of every target vertex from every source under their action.",
            ),
            p(
                "The independent classifier replaces set partitions by surjective color assignments and canonicalizes each graph under all n! vertex permutations. It freezes the labelled multiplicities, canonical codes, endomorphism counts, minimum ranks, minimum profiles, and transitivity results. Agreement is therefore structural, not merely agreement on a final Boolean answer.",
            ),
            h1("Appendix B. Independent checks"),
            p(
                "The primary six-state Python verifier closes the generated semigroup in both multiplication directions and checks every minimum-rank continuation. The C++ verifier instead performs breadth-first search on the actual prefix-product chain from the identity. The family implementations use separately written constructors and closure logic. Assertions are required: Python refuses optimized execution under -O, and C++ refuses compilation with NDEBUG.",
            ),
            p(
                "AddressSanitizer and UndefinedBehaviorSanitizer builds are part of the canonical reproduction. Users whose compiler lacks those facilities may pass --no-sanitizers, but the script labels that run as reduced verification. The manifest detects accidental drift; it is not a signature and does not establish authorship or publication priority. A signed Git tag or archival DOI should be added at public release.",
            ),
        ]
    )

    story.extend(
        [
            h1("Author's note on provenance"),
            p(
                "This paper is the output of a mostly autonomous experiment in AI-assisted mathematical research. OpenAI's GPT-5.6 Sol searched for a tractable problem, developed the claimed result, wrote the supporting software and verification design, and drafted the manuscript with minimal human intervention. The human project lead initiated the experiment through an OpenAI subscription, prompted occasionally when the process reached stopping points, set disclosure and release standards, and chose to make the result available for review. The work is not presented as primarily human mathematical research or as evidence of conventional mathematical training. Readers should treat the result as a reproducible research claim awaiting specialist review. Deterministic code and frozen artifacts are supplied so the claims can be assessed on their evidence. Specialist criticism is invited. Demonstrated errors will be documented and corrected, or the affected claims withdrawn.",
                BODY_SMALL,
            ),
            p(
                "<b>Repository and review materials.</b> <link href='https://github.com/lukekabbash/finite-grand-couplings' color='#294C69'>github.com/lukekabbash/finite-grand-couplings</link>",
                BODY_SMALL,
            ),
            h1("References"),
            reference(
                1,
                "G. R. Grimmett and M. Holmes, “Coalescence in Markov Chains,” <i>Journal of Theoretical Probability</i> 39 (2026), Article 49. <link href='https://doi.org/10.1007/s10959-026-01500-w' color='#294C69'>doi:10.1007/s10959-026-01500-w</link>.",
            ),
            reference(
                2,
                "P. Diaconis and D. Freedman, “Iterated Random Functions,” <i>SIAM Review</i> 41(1) (1999), 45-76. <link href='https://doi.org/10.1137/S0036144598338446' color='#294C69'>doi:10.1137/S0036144598338446</link>.",
            ),
            reference(
                3,
                "B. Steinberg, “A Theory of Transformation Monoids: Combinatorics and Representation Theory,” <i>Electronic Journal of Combinatorics</i> 17(1) (2010), R164, 56 pp. <link href='https://doi.org/10.37236/436' color='#294C69'>doi:10.37236/436</link>.",
            ),
            reference(
                4,
                "P. J. Cameron and P. A. Kazanidis, “Cores of Symmetric Graphs,” <i>Journal of the Australian Mathematical Society</i> 85(2) (2008), 145-154. <link href='https://doi.org/10.1017/S1446788708000815' color='#294C69'>doi:10.1017/S1446788708000815</link>.",
            ),
            reference(
                5,
                "P. J. Cameron, “Dixon's Theorem and Random Synchronization,” <i>Discrete Mathematics</i> 313(11) (2013), 1233-1236. <link href='https://doi.org/10.1016/j.disc.2012.06.002' color='#294C69'>doi:10.1016/j.disc.2012.06.002</link>.",
            ),
            reference(
                6,
                "A. Schaefer, “Generating Sets of the Kernel Graph and the Inverse Problem in Synchronization Theory,” arXiv:1601.04295v2 (2016). <link href='https://doi.org/10.48550/arXiv.1601.04295' color='#294C69'>doi:10.48550/arXiv.1601.04295</link>.",
            ),
            reference(
                7,
                "J. Araújo and P. J. Cameron, “Primitive Groups Synchronize Non-Uniform Maps of Extreme Ranks,” <i>Journal of Combinatorial Theory, Series B</i> 106 (2014), 98-114. <link href='https://doi.org/10.1016/j.jctb.2014.01.006' color='#294C69'>doi:10.1016/j.jctb.2014.01.006</link>.",
            ),
            reference(
                8,
                "G. Budzban and P. Feinsilver, “A Hierarchical Structure of Transformation Semigroups with Applications to Probability Limit Measures,” <i>Journal of Difference Equations and Applications</i> 18(8) (2012), 1405-1434. <link href='https://doi.org/10.1080/10236198.2011.639365' color='#294C69'>doi:10.1080/10236198.2011.639365</link>.",
            ),
            reference(
                9,
                "J. G. Propp and D. B. Wilson, “Exact Sampling with Coupled Markov Chains and Applications to Statistical Mechanics,” <i>Random Structures &amp; Algorithms</i> 9(1-2) (1996), 223-252. <link href='https://doi.org/10.1002/(SICI)1098-2418(199608/09)9:1/2%3C223::AID-RSA14%3E3.0.CO;2-O' color='#294C69'>doi:10.1002/(SICI)1098-2418(199608/09)9:1/2&lt;223::AID-RSA14&gt;3.0.CO;2-O</link>.",
            ),
        ]
    )
    return story


def build():
    doc, width = make_document(
        OUTPUT,
        title=TITLE_TEXT,
        author=AUTHOR_TEXT,
        subject="Finite grand couplings, exact counterexample family, and state minimality",
        short_title=SHORT_TITLE,
    )
    doc.build(build_story(width))
    print(OUTPUT)


if __name__ == "__main__":
    build()
