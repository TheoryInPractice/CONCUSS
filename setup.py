from setuptools import setup


setup(
    name='CONCUSS', 
    version='1.0', 
    description='Combatting Network Complexity Using Structural Sparsity',
    author= 'Michael P. O\'Brien, Clayton G. Hobbs, Kevin Jasnik, Felix Reidl, Nishant G. Rodrigues, and Blair D. Sullivan',
    author_email='blair_sullivan@ncsu.edu', 
    url='https://www.github.com/theoryinpractice/CONCUSS',
    license='BSD',
    packages=['concuss'], 
    package_dir={
                'concuss':''
                },
    extras_require={
                'test':['networkx'], 
                'gexf':['beautifulsoup'],
                'graphml':['beautifulsoup']
                },
    classifiers=[ 
                'License :: OSI Approved :: BSD License', 
                'Intended Audience :: Science/Research',
                'Programming Language :: Python :: 2.7',
                ]
    )
