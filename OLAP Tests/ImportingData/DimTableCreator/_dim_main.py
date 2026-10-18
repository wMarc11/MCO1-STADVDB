import dim_date
import dim_flag
import dim_location
import dim_payment
import dim_ratecode
import dim_time
import dim_vendor

db_name = "olaptest_dw5_pivot"

dim_date.main(db_name)
dim_flag.main(db_name)
dim_location.main(db_name)
dim_payment.main(db_name)
dim_ratecode.main(db_name)
dim_time.main(db_name)
dim_vendor.main(db_name)
