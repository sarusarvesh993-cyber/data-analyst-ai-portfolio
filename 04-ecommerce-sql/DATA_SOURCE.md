# Data source and license

## Dataset

**Brazilian E-Commerce Public Dataset by Olist**

- Source page: <https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>
- Publisher: Olist
- Version used: Kaggle dataset version 2
- Coverage: approximately 100,000 anonymized orders placed from 2016 to 2018
- Geography: Brazil
- License: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

The dataset contains separate tables for orders, customers, items, payments,
reviews, products, sellers, and product-category translations. Olist states
that the records are real commercial data, anonymized, with identifying names
replaced.

## Use in this repository

Raw files are downloaded directly from Kaggle by `download_data.py` and are
excluded from Git. The committed files under `outputs/` are small analytical
aggregates derived from the source and are provided for non-commercial
portfolio demonstration with attribution under the same CC BY-NC-SA terms.

## Important limitations

- The data are historical and end in 2018.
- Customer, company, and partner identifiers are anonymized.
- Monetary values are in Brazilian reais (BRL).
- `item_gmv` in this project is the sum of listed item prices for delivered
  orders. It is a marketplace sales-volume measure, not Olist's accounting
  revenue or profit.
- Association between late delivery and review score is not a causal estimate.
