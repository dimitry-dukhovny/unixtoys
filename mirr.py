#!/usr/local/bin/python -i
def schedule(principal,i,n,m=1):
	"""
principal
interest
years
payments per year
	"""
	PMT = principal / PVIFA(i,n,m)
	print("""
YEAR	ANNUITY		INT		PRINC		BALANCE
""")
	for f in range(n):
		year = f+1
		i_exp = principal * i
		p_exp = PMT - i_exp
		principal = principal - p_exp
		print("%.2f	%.2f		%.2f		%.2f		%.2f" % (year, PMT, i_exp, p_exp, principal))

def FVIFA(i,n):
	"""
interest
years
	"""
	FVIFA=0
	for t in range(n):
		FVIFA=FVIFA+(1+i)**t
	return FVIFA

def PVIF(i,n,m=1):
	"""
interest
years
payments per year
	"""
	PVIF = 1 / ((1 + i/m)**(m*n))
	return PVIF

def FVIF(i,n,m=1):
	"""
interest
years
payments per year
	"""
	FVIF = (1 + i/m)**(m*n)
	return FVIF

def FV(PV,i,n,m=1):
	"""
present value
interest
years
optional payments per year
	"""
	FV = PV * ((1 + i/m)**(m*n))
	return FV

def PV(FV,i,n,m=1):
	"""
future value
interest
years
optional payments per year
	"""
	PV = FV / ((1 + i/m)**(m*n))
	return PV

def PVIFA(i,n,m=1):
	"""
interest
years
optional payments per year"
	"""
	PVIFA = (1 - (1 / ((1 + i / m)**(m * n)))) / i
	return PVIFA

def bondDuration(n, C, k, P):
	"""
years to maturity
cash flow expected (list)
bondholders required rate of return
present value
	"""
	value = 0
	for f in range(n):
		t = f+1
		value = t * C[t] / ((1 + k)**t)
	duration = value/P

def bondValue(n, M, I, k,m=1):
	"years, face/coupon value, coupon rate, required rate of return,payments per year"
	PMT = I * M
	V = PMT * PVIFA(k,n,m) + M * PVIF(k,n,m)
	return V

def k_increment(k, x):
	"called by YTM"
	print("adding",10**(-x),"to k")
	k = k+10**(-x)
	return k

def k_decrement(k, x):
	"called by YTM"
	print("subtracting",10**(-x),"from k")
	k = k-10**(-x)
	return k

def YTM(PV, FV, n, I, m=1, precision=16):
	"""
Yield to Maturity:
present value or price
future value
years
annual interest
payments per year
significant figures
	"""
	V=FV
	k=I
	for x in range(3,precision+1):
		x = x + 1
		if V > PV:
			while V > PV:
				k = k+10**(-x)
				V = bondValue(n, FV, I, k, m)
		elif V < PV:
			while V < PV:
				k = k-10**(-x)
				V = bondValue(n, FV, I, k, m)
	YTM = k
	return YTM, bondValue(n, FV, I, k, m)

def valueCF(CF, IRR, n):
	"""
cash flow array
internal rate of return
number of years
	"""
	V = 0
	for t in range(n):
		V = V + CF[t]/((1 + IRR)**(t+1))
	return V

def IRR(IO, n, CF=None):
	"""
initial outlay
number of years
cash flow array
	"""
	if CF==None:
		CF=[]
		print("Enter cash flows:  ")
		for f in range(n):  CF.append(int(raw_input()))
	k = 0.5
	V = valueCF(CF, k, n)
	for x in range(3,16):
		x = x + 1
		if V > IO:
			while V > IO:
				k = k+10**(-x)
				V = valueCF(CF, k, n)
		elif V < IO:
			while V < IO:
				k = k-10**(-x)
				V = valueCF(CF, k, n)
	IRR=k
	return IRR, (str(IRR*100)+"%")

def perpetuity(A, r):
  """
  A = annual payment
  r = discount rate
  returns present value
  """
  return(A/r)
  
def growing_perpetuity(A, r, g, y=0):
  """
  A = initial annual payment
  r = discount rate
  g = growth rate
  y = year number
  returns present value
  """
  return((A / (1 + r)**y)/(r-g))

def annuity(A, r, g, t):
  """
  A = annual payment
  r = discount rate
  t = time periods
  returns present value
  """
  return((A/r) * (1 - 1/((1+r)**t)))

def growing_annuity(A, r, g, t, y=0):
  """
  A = annual payment
  r = discount rate
  g = growth rate
  t = time periods
  returns present value
  """
  val = ((A/(r-g)) * (1 - ((1+g)/(1+r))**t))
  if y:
    val = PV(val, r, y-1)
  return(val)
