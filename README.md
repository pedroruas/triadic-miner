
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<p align="center"><img align="center" width="380" src="./logos/logo_triadic_miner_white.png#gh-dark-mode-only"/></p>
<p align="center"><img align="center" width="380" src="./logos/logo_triadic_miner_black.png#gh-light-mode-only"/></p>

<p align="center"><b>A Python library for mining patterns from Triadic Concepts.</b></p>

---

# Triadic Miner

Triadic Miner leverages **Triadic Concept Analysis (TCA)** as a framework for discovering patterns expressed by:

- **Triadic Concepts**
- **Hasse Diagrams** (for navigation and exploration)
- **Association Rules** (including different types of triadic implications)

---

## 🚀 Key Features

- **Link Discovery Between Triadic Concepts**  
  Using the [_T-iPred_](https://link.springer.com/article/10.1007/s10472-022-09784-4) algorithm.

- **Triadic Generators Computation**

- **Five Types of Triadic Implications and Association Rules:**
  - Biedermann Conditional Attribute Implication (**BCAI**)
  - Biedermann Attributional Condition Implication (**BACI**)
  - Biedermann Conditional Attribute Association Rule (**BCAAR**)
  - Biedermann Attributional Condition Association Rule (**BACAR**)
  - Extensional Implications

- **Two Triadic Concept Relevancy Scores:**
  - **Concept Stability**
  - **Separation Index**

- **Hasse Diagram Generation:**  
  For visualization and exploration of Triadic Concepts and their upper and lower covers.

---

## 📦 Installation

You will need [Git](https://git-scm.com) and [Python 3.10+](https://www.python.org/downloads/) installed.

From your terminal:

```bash
# Clone this repository
git clone https://github.com/pedroruas/triadic-miner.git

# Navigate into the project directory
cd triadic-miner

# Install the package in editable (development) mode
pip install -e .
```

This will also install all required dependencies, as specified in `setup.py`.

---

## ⚙️ How to Run

After installation, you can run the miner as follows:

```bash
python main.py
```

Before running, configure the `configs.json` file to specify:

- Input file(s)
- Output directory (where all generated files will be saved)
- Execution parameters (e.g., which modules to run)

---

## 📂 Data Input Format

The input file should contain Triadic Concepts with the following structure:

- One concept per line
- Elements of each dimension (objects, attributes, conditions) separated by commas
- Dimensions separated by spaces
- Empty sets represented by `'ø'`

**Example input:**

```
obj1 att1 cond1
obj2 att3 cond2,cond3
obj3 att4,att5 cond1
obj1,obj2,obj3 att2,att3 cond2,cond3
```

We recommend using the [Data Peeler](https://homepages.dcc.ufmg.br/~lcerf/fr/prototypes.html#d-peeler) algorithm to compute the Triadic Concepts. Its output complies with this format.

---

## 📊 Hasse Diagram Visualization

For the Hasse Diagram representation, the framework outputs a `.graphml` file, following the [GraphML](http://graphml.graphdrawing.org/) standard (XML-based).

We recommend using the [yEd Graph Editor](https://www.yworks.com/products/yed) to visualize and explore the diagram.

### Visualization Steps in yEd:

1. Open the `.graphml` file in yEd.
2. Press `Ctrl + A` (or `Cmd + A` on Mac) to select all nodes.
3. Go to **Tools > Fit Node to Label**, then click OK.
4. Go to **Layout > Hierarchical**, then click OK.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn and innovate. Any contributions you make are **greatly appreciated**.

If you have suggestions for improvements, feel free to:

1. Fork the repository
2. Create a feature branch:  
   `git checkout -b dev/YourFeatureName`
3. Commit your changes:  
   `git commit -m 'Add some feature'`
4. Push to your branch:  
   `git push origin dev/YourFeatureName`
5. Open a Pull Request

Alternatively, you can open an Issue labeled as **enhancement**.

---

## 📬 Contact

**Pedro Ruas, Ph.D** – pedrohbruas@gmail.com  
**Rokia Missaoui, Ph.D** – Rokia.Missaoui@uqo.ca

---

## 🎓 Acknowledgment

This project was supported by the **Natural Sciences and Engineering Research Council of Canada (NSERC)**.

---

## 📄 License

Distributed under the MIT License. See `LICENSE.txt` for more information.

[linkedin-url]: https://www.linkedin.com/in/pedro-ruas-666a7365/
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/pedroruas/triadic-miner/blob/main/LICENSE.md
