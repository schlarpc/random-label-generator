import argparse
import io
import random
import string

import fpdf
import PyPDF2


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--page", "-p", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0x1455E8F9)
    parser.add_argument("--template", default="Avery4221RoundLabels.pdf")
    parser.add_argument("--font-family", default="Consolas")
    parser.add_argument("--font-file", default="consola.ttf")
    parser.add_argument("--x-margin", type=int, default=30)
    parser.add_argument("--x-interval", type=int, default=72)
    parser.add_argument("--x-count", type=int, default=8)
    parser.add_argument("--y-margin", type=int, default=61)
    parser.add_argument("--y-interval", type=int, default=72)
    parser.add_argument("--y-count", type=int, default=10)
    parser.add_argument("--label-duplicates", type=int, default=2)
    parser.add_argument("--alphabet", default=string.ascii_uppercase)
    parser.add_argument("--label-length", type=int, default=4)
    parser.add_argument("--font-size", type=int, default=20)
    parser.add_argument("--info-x", type=int, default=10)
    parser.add_argument("--info-y", type=int, default=10)
    parser.add_argument("--cell-width", type=int, default=100)
    parser.add_argument("--cell-height", type=int, default=20)
    parser.add_argument("--output", default="output.pdf")
    return parser.parse_args()


def main():
    args = get_args()
    rng = random.Random(args.seed)

    seen_items = set()

    for page_number in (n + 1 for n in range(args.page)):
        scratch = fpdf.FPDF(format="letter", unit="pt")
        scratch.add_page()
        scratch.add_font(args.font_family, fname=args.font_file, uni=True)
        scratch.set_font(args.font_family, size=args.font_size)

        scratch.set_xy(args.info_x, args.info_y)
        scratch.cell(
            args.cell_width,
            args.cell_height,
            txt=f"Page {page_number} (seed = {args.seed})",
        )

        item_queue = []

        for x_offset in (x * args.x_interval for x in range(args.x_count)):
            for y_offset in (y * args.y_interval for y in range(args.y_count)):
                scratch.set_xy(args.x_margin + x_offset, args.y_margin + y_offset)
                if not item_queue:
                    while True:
                        item = "".join(
                            rng.choice(args.alphabet) for _ in range(args.label_length)
                        )
                        if item not in seen_items:
                            seen_items.add(item)
                            break
                    item_queue = [item] * args.label_duplicates

                scratch.cell(args.cell_width, args.cell_height, txt=item_queue.pop())
        overlay_bytes = scratch.output(dest="S").encode("latin-1")

    with open(args.template, "rb") as f:
        template_bytes = f.read()

    template_page = PyPDF2.PdfFileReader(io.BytesIO(template_bytes)).getPage(0)
    overlay_page = PyPDF2.PdfFileReader(io.BytesIO(overlay_bytes)).getPage(0)
    template_page.mergePage(overlay_page)
    with open(args.output, "wb") as f:
        writer = PyPDF2.PdfFileWriter()
        writer.addPage(template_page)
        writer.write(f)


if __name__ == "__main__":
    main()
