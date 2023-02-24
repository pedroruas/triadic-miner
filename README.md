
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<h1 align="center">
  Triadic Miner
  <br>
</h1>

<h4 align="center">A <b>Python</b> library to mine <b>Triadic Concepts</b>.</h4>

<br>


In this project, we use Triadic Concept Analysis as a framework to discover patterns expressed by <b>Triadic Concepts</b>, the <b>Hasse diagram</b> navigation/exploration, and by <b>Association Rules</b> (including implications).


## Key Features

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


## How to Use

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
<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b dev/NewFeature`)
3. Commit your Changes (`git commit -m 'Add some NewFeature'`)
4. Push to the Branch (`git push origin dev/NewFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Contact
Pedro Ruas, Ph.D - pedrohbruas@gmail.com

Rokia Missaoui, Ph.D - Rokia.Missaoui@uqo.ca
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License
Distributed under the MIT License. See `LICENSE.txt` for more information.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

[linkedin-url]: https://www.linkedin.com/in/pedro-ruas-666a7365/
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/pedroruas/triadic-miner/blob/main/LICENSE.md

