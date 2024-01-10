
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<p align="center"><img align="center" width="380" src="./logos/logo_triadic_miner_white.png#gh-dark-mode-only"/></p>
<p align="center"><img align="center" width="380" src="./logos/logo_triadic_miner_black.png#gh-light-mode-only"/></p>
<!-- <h1 align="center">
  Triadic Pattern Miner
  <br>
</h1> -->

<p align="center">A <b>Python</b> library to mine patterns in <b>Triadic Concepts</b>.</p>


In this project, we use Triadic Concept Analysis as a framework to discover patterns expressed by <b>Triadic Concepts</b>, the <b>Hasse diagram</b> (for navigation/exploration), and by <b>Association Rules</b> (including implications).


# Key Features

* Compute links between Triadic Concepts using the [_T-iPred_](https://link.springer.com/article/10.1007/s10472-022-09784-4) algorithm  
* Compute Triadic Generators
* Compute 5 kinds of Triadic Implications and Association Rules:
    - Biedermann Conditional Attribute Implication (BCAI)
    - Biedermann Attributional Condition Implication (BACI)
    - Biedermann Conditional Attribute Association Rule (BCAAR)
    - Biedermann Attributional Condition Association Rule (BACAR)
    - Extensional Implications
* Compute 2 Triadic Concept relevancy scores:
    - Concept Stability
    - Separation Index
* Construct a Hasse Diagram to visualize and explore Triadic Concepts and their upper and lower covers

# How to Use

To clone and run this application, you will need [Git](https://git-scm.com) and [Python 3.10+](https://www.python.org/downloads/) installed on your computer. From your command line:

```bash
# Clone this repository
$ git clone https://github.com/pedroruas/triadic-miner.git

# Go into the repository
$ cd triadic-miner

# Install dependencies
$ pip install -r requirements.txt

# Run the app
$ python main.py
```
In the <i>'configs.json'</i> file, you can specify the input file(s), the output directory (where all generated files will be saved), and also some execution parameters.

## Data input

The input of our framework is a file with all the Triadic Concepts.
This file should contain:

- One concept per line
- The elements of each dimension (objects, attributes, and conditions) are separated by commas
- The dimensions are separated by spaces
- The empty set is represented by 'ø'

An example of an input file is:

```bash
obj1 att1 cond1
obj2 att3 cond2,cond3
obj3 att4,att5 cond1
obj1,obj2,obj3 att2,att3 cond2,cond3
```

We recommend using the [Data Peeler](https://homepages.dcc.ufmg.br/~lcerf/fr/prototypes.html#d-peeler) algorithm to compute the Triadic Concepts (its output satisfies all the requirements mentioned above).


## Hasse diagram visualization

For the Hasse Diagram representation, we are using the [GraphML](http://graphml.graphdrawing.org/) ([GraphML Primer](http://graphml.graphdrawing.org/primer/graphml-primer.html)) file format. This is an open standard based on XML, and is supported by Python libraries such as [NetworkX](https://networkx.org/). 
We recommend the [yEd Graph Editor](https://www.yworks.com/products/yed) software to visualize and explore the Hasse Diagram.

After creating the <i>.graphml</i> file, open yEd Graph Editor and follow these steps:

- Use Ctrl + A (Cmd + A on Mac) to select all nodes
- Go to Tools > Fit Node to Label > click OK
- Go to Layout > Hierarchical > click OK

# Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b dev/NewFeature`)
3. Commit your Changes (`git commit -m 'Add some NewFeature'`)
4. Push to the Branch (`git push origin dev/NewFeature`)
5. Open a Pull Request


# Contact
Pedro Ruas, Ph.D - pedrohbruas@gmail.com

Rokia Missaoui, Ph.D - Rokia.Missaoui@uqo.ca


# License
Distributed under the MIT License. See `LICENSE.txt` for more information.

[linkedin-url]: https://www.linkedin.com/in/pedro-ruas-666a7365/
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/pedroruas/triadic-miner/blob/main/LICENSE.md

