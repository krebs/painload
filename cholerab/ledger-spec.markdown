# Ledger Specification

## Transaction Record

### External Representation

    DATE DESTINATION-ACCOUNT SOURCE-ACCOUNT AMOUNT UNIT [COMMENT...]

  where
  - `DATE` has the form `YYYY-MM-DD`
  - `AMOUNT` is a non-negative, decimal number

### Example

    2013-01-01 krebs-ml amazon 30 EUR C0DE-AAAA-BBBB-CCCC
    2013-02-02 momo krebs-ml 50 EUR C0DE-AAAA-BBBB-CCCC
    2013-02-02 mindfactory momo 80 EUR
