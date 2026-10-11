"""Kept for older instructions: same as publish_book.py --book the_inner_being."""
import sys

import publish_book

if __name__ == "__main__":
    sys.argv[1:1] = ["--book", "the_inner_being"]
    publish_book.main()
