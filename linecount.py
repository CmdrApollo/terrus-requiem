import glob

lc = lambda x: len(open(x, 'r', encoding='utf-8').readlines())

stuff = glob.glob('**/*.py', recursive=True)

stuff = sorted(stuff, key=lc, reverse=True)

for x in stuff: print(f"'{x}': {lc(x)}")

print(f"\nCurrent Project Line Count: {sum([lc(x) for x in stuff]) - lc(__file__)}")