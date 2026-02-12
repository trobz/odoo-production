This module overrides the credit amount to set the attribute "digits" to 0
 instead of the default value (which is 2). This allows to handle credit
 amounts as integers in the Point of Sale interface, which is useful in
 scenarios where credit is managed in whole units (e.g., points, credits)
 rather than fractional currency values.