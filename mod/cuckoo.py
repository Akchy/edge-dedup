from cuckoo_filter import CuckooFilter

# Create a filter with a capacity of 100 items
cf = CuckooFilter(capacity=100)

# Add items to the filter
cf.insert("item1")
cf.insert("item2")
cf.insert("item3")

# Check if an item is in the filter
print(cf.contains("item1")) # True
print(cf.contains("item4")) # False

# Remove an item from the filter
cf.delete("item2")

# Check if an item is in the filter
print(cf.contains("item2")) # False
