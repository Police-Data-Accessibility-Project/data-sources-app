

## Design Notes

At present, sync updates follow the principle of full overwrites, for the following reasons:
- The amount of updates expected are small
- Partial updates requires a considerably higher level of logic, increasing potential for bugs
- The data in each update is fairly small as is
