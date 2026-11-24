#!/usr/bin/env python3
"""Python re-implementation of cobol/src/program.cbl (BOOKFORUM)."""

import os
import sys

ACC_REC = 34   # 4 + 20 + 10
BOOK_REC = 28  # 4 + 20 + 4
TRANS_REC = 22 # 4 + 10 + 4 + 4
INPUT_REC = 22 # 4 + 4 + 4 + 10


def read_fixed_records(path, rec_size):
    with open(path, "rb") as f:
        data = f.read()
    return [data[i:i + rec_size] for i in range(0, len(data), rec_size) if data[i:i + rec_size]]


def parse_amount(buf):
    s = buf.decode("latin-1").strip()
    if not s:
        return 0
    try:
        return int(s)
    except ValueError:
        digits = "".join(c for c in s if c.isdigit())
        return int(digits) if digits else 0


def fmt_amount(val, width=10):
    if val < 0:
        val = 0
    return f"{val:0{width}d}".encode("latin-1")


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base, "src", "INPUT.DAT")
    accounts_path = os.path.join(base, "data", "ACCOUNTS.DAT")
    books_path = os.path.join(base, "data", "BOOKS.DAT")
    trans_path = os.path.join(base, "data", "TRANSACTIONS.DAT")

    with open(input_path, "rb") as f:
        inp = f.read()
    if not inp:
        print("Error: Input file is empty")
        return

    inp = inp.ljust(INPUT_REC, b" ")
    buyer_id = inp[0:4]
    seller_id = inp[4:8]
    book_id = inp[8:12]
    amount = parse_amount(inp[12:22])

    accounts = read_fixed_records(accounts_path, ACC_REC)
    books = read_fixed_records(books_path, BOOK_REC)

    buyer_found = any(r[0:4] == buyer_id for r in accounts)
    seller_found = any(r[0:4] == seller_id for r in accounts)
    book_found = False
    valid_owner = False
    for r in books:
        if r[0:4] == book_id:
            book_found = True
            if r[24:28] == seller_id:
                valid_owner = True

    if not (buyer_found and seller_found and book_found and valid_owner):
        print("Transaction failed due to validation errors")
        return

    new_accounts = []
    for r in accounts:
        rid = r[0:4]
        name = r[4:24]
        bal = parse_amount(r[24:34])
        if rid == buyer_id:
            bal -= amount
        if rid == seller_id:
            bal += amount
        new_accounts.append(rid + name + fmt_amount(bal, 10))
    with open(accounts_path, "wb") as f:
        f.write(b"".join(new_accounts))

    new_books = []
    for r in books:
        bid = r[0:4]
        title = r[4:24]
        owner = r[24:28]
        if bid == book_id:
            owner = buyer_id
        new_books.append(bid + title + owner)
    with open(books_path, "wb") as f:
        f.write(b"".join(new_books))

    trans_rec = book_id + fmt_amount(amount, 10) + seller_id + buyer_id
    with open(trans_path, "ab") as f:
        f.write(trans_rec)

    print("Transaction completed successfully")


if __name__ == "__main__":
    main()
