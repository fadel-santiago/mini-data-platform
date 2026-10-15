from __future__ import annotations

import argparse
import csv
import os
import random
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo


CUSTOMERS = (
    ("C001", "Atelier Horizon", "pme", "IDF"),
    ("C002", "Maison Lenoir", "pme", "OUEST"),
    ("C003", "Groupe Valmont", "eti", "SUD"),
    ("C004", "Buro Nova", "tpe", "NORD"),
    ("C005", "Alpes Services", "pme", "EST"),
    ("C006", "Comptoir Azur", "tpe", "SUD"),
    ("C007", "Logis & Co", "pme", "OUEST"),
    ("C008", "TechniPro", "eti", "IDF"),
    ("C009", "Delta Conseil", "pme", "NORD"),
    ("C010", "Manufacture Artois", "eti", "EST"),
    ("C011", "Studio Rivoli", "tpe", "IDF"),
    ("C012", "Nature Distribution", "pme", "SUD"),
    ("C013", "Armor Equipement", "pme", "OUEST"),
    ("C014", "Hexagone Retail", "eti", "NORD"),
    ("C015", "Vosges Habitat", "pme", "EST"),
    ("C016", "Pixel & Papier", "tpe", "IDF"),
)

PRODUCTS = (
    ("P001", "Chaise ergonomique", "mobilier", 118, 229),
    ("P002", "Bureau reglable", "mobilier", 285, 549),
    ("P003", "Caisson mobile", "mobilier", 72, 139),
    ("P004", "Ecran 27 pouces", "informatique", 168, 329),
    ("P005", "Station accueil USB-C", "informatique", 76, 149),
    ("P006", "Clavier compact", "informatique", 31, 69),
    ("P007", "Lampe de bureau", "accessoires", 26, 59),
    ("P008", "Support ordinateur", "accessoires", 22, 49),
    ("P009", "Table reunion", "mobilier", 410, 829),
    ("P010", "Webcam HD", "informatique", 43, 99),
    ("P011", "Casque audio", "informatique", 54, 119),
    ("P012", "Tableau acoustique", "accessoires", 95, 199),
)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def iso_at(day: date, minutes: int = 0) -> str:
    return datetime.combine(day, time(8, 0), tzinfo=timezone.utc).replace(
        minute=minutes % 60
    ).isoformat()


def generate(output_dir: Path, as_of: date) -> None:
    rng = random.Random(42)
    start = as_of - timedelta(days=110)

    customers = [
        {
            "customer_id": customer_id,
            "company_name": name,
            "segment": segment,
            "region": region,
            "created_at": (start - timedelta(days=90 + index * 7)).isoformat(),
            "updated_at": iso_at(as_of - timedelta(days=index % 9), index),
        }
        for index, (customer_id, name, segment, region) in enumerate(CUSTOMERS)
    ]

    inventory = []
    stock_levels = (0, 4, 62, 18, 7, 94, 12, 0, 5, 38, 81, 9)
    reorder_points = (8, 4, 15, 12, 10, 20, 12, 6, 3, 9, 14, 10)
    for index, ((product_id, name, category, cost, _), stock, reorder) in enumerate(
        zip(PRODUCTS, stock_levels, reorder_points)
    ):
        inventory.append(
            {
                "product_id": product_id,
                "product_name": name,
                "category": category,
                "stock_quantity": stock,
                "reorder_point": reorder,
                "unit_cost": f"{cost:.2f}",
                "updated_at": iso_at(as_of, index),
            }
        )

    orders: list[dict[str, object]] = []
    lines: list[dict[str, object]] = []
    invoices: list[dict[str, object]] = []
    channels = ("commercial", "web", "partenaire")
    statuses = ("delivered", "delivered", "shipped", "confirmed", "cancelled")

    for number in range(1, 85):
        order_id = f"O{number:04d}"
        order_date = start + timedelta(days=rng.randint(0, 108))
        customer = rng.choice(CUSTOMERS)
        status = rng.choice(statuses)
        updated_day = min(order_date + timedelta(days=rng.randint(0, 7)), as_of)
        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer[0],
                "order_date": order_date.isoformat(),
                "status": status,
                "channel": rng.choice(channels),
                "updated_at": iso_at(updated_day, number),
            }
        )

        total = Decimal("0")
        for line_number, product in enumerate(rng.sample(PRODUCTS, rng.randint(1, 3)), 1):
            quantity = rng.randint(1, 7)
            price = Decimal(str(product[4]))
            cost = Decimal(str(product[3]))
            total += price * quantity
            lines.append(
                {
                    "order_id": order_id,
                    "line_id": line_number,
                    "product_id": product[0],
                    "quantity": quantity,
                    "unit_price": f"{price:.2f}",
                    "unit_cost": f"{cost:.2f}",
                    "updated_at": iso_at(updated_day, number + line_number),
                }
            )

        if status != "cancelled":
            due_date = order_date + timedelta(days=30)
            paid = rng.random() < 0.64
            if paid:
                paid_date = due_date + timedelta(days=rng.randint(-10, 18))
                invoice_status = "paid"
            else:
                paid_date = None
                invoice_status = "overdue" if due_date < as_of else "open"
            invoices.append(
                {
                    "invoice_id": f"INV-{number:04d}",
                    "order_id": order_id,
                    "issued_date": order_date.isoformat(),
                    "due_date": due_date.isoformat(),
                    "paid_date": paid_date.isoformat() if paid_date else "",
                    "amount": f"{total:.2f}",
                    "status": invoice_status,
                    "updated_at": iso_at(
                        min(paid_date or max(order_date, as_of - timedelta(days=3)), as_of),
                        number,
                    ),
                }
            )

    write_csv(output_dir / "crm_customers.csv", list(customers[0]), customers)
    write_csv(output_dir / "crm_orders.csv", list(orders[0]), orders)
    write_csv(output_dir / "erp_order_lines.csv", list(lines[0]), lines)
    write_csv(output_dir / "erp_inventory.csv", list(inventory[0]), inventory)
    write_csv(output_dir / "finance_invoices.csv", list(invoices[0]), invoices)

    print(
        f"Donnees generees dans {output_dir}: {len(customers)} clients, "
        f"{len(orders)} commandes, {len(lines)} lignes, {len(invoices)} factures."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Genere les sources de demonstration PME")
    parser.add_argument("--output", type=Path, default=Path("data/sources"))
    business_timezone = ZoneInfo(os.getenv("BUSINESS_TIMEZONE", "Europe/Paris"))
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        default=datetime.now(business_timezone).date(),
    )
    args = parser.parse_args()
    generate(args.output, args.as_of)


if __name__ == "__main__":
    main()

