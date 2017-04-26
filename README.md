# pimc_pylib
pimc_pylib is the Python library for Parametric Interval Markov Chains (PIMC) Verification.
This library allows to: 
* generate PIMCs from MCs (see. Section PIMC generator)
* generate CSP models for PIMC verification (see. Section PIMC modeler)

## Installation
- Python 3 is required
- [PRISM](http://www.prismmodelchecker.org) is required for using PIMC generator
- Edit the ```config.ini``` file to set the location of your PRISM executable/binary.

## New!
Check the "data/QEST17" folder and its README document to retreive informations relative to this submission.

## Run
Launch Python scripts ```pimc_generator``` and ```pimc_modeler``` in the ```src``` folder to run respectively the PIMC generator and the PIMC modeler. Both commands have the ```-h``` option for printing help and usage.
```console
> src/pimc_generator [-h] <generation_file> [-o <output_directory>]
> src/pimc_modeler [-h] -i <pimc_file> (-smt | -milp | -vmcai16) [r | d] -o <output_file> 
```

## PIMC generator
The PIMC generator transforms a Discrete Time Markov Chain (MC for short) to a Parametric Interval Markov Chain. The script takes one configuration file as argument. The configuration must be written in the JSON format. It contains the location file of the MC to consider and how many parameters and intervals must be added from the MC to generate a PIMC. The MC file must be written in the [PRISM language](http://www.prismmodelchecker.org/). In order to generate a PIMC, the five following values must be set in the generator configuration input file:
- the location of the PRISM model (key: ```prismFile```)
- the constants in the PRISM model associated with values (key: ```prismConstants```)
- the number of parameters to insert in the PIMC (key: ```nbParameters```)
- the ratio value for the number of intervals over the number of transitions in the PIMC (key: ```ratioIntervals```)
- the ratio value for the number of parameters over the number of interval endpoints in the PIMC (key: ```ratioParameters```)

The values associated to the keys can be either one value or a list of values. In the case of a list of values, the PIMC generator will consider all the possible combinations of values between all the keys. Some examples of configuration files for PIMC generation can be found in [data/generator/config](https://github.com/anicet-bart/pimc_pylib/tree/master/data/generator/config). Some examples of PRISM files can be found in [data/generator/inputs](https://github.com/anicet-bart/pimc_pylib/tree/master/data/generator/inputs) (from [PRISM benchmarks](http://www.prismmodelchecker.org/benchmarks/models.php#dtmcs)).

The following configuration file will generate 12 PIMCs:
```json
{
	"prismFile"     : "data/generator/inputs/brp.pm",
	"prismConstants": 
	{
		"N" : [16, 32],
		"MAX" : 4
	},
	"nbParameters"   : [2, 5], 
	"ratioIntervals" : 0.2,
	"ratioParameters": [0.05, 0.1, 0.2]
}
```

**Warning:** do not forget to set the location of your PRISM executable in the ```config.ini``` file.

## PIMC modeler
The PIMC modeler takes a PIMC as argument and returns a CSP model answering the existential consistency problem for this PIMC.
Supported modellings are:
* modelling from [1] into the [SMT-LIB 2 format](http://smtlib.cs.uiowa.edu) (option ```-vmcai16```)
* Our Mec modelling into the [SMT-LIB 2 format](http://smtlib.cs.uiowa.edu) (option ```-smt```)
* Our Mec modelling into the [CPLEX LP file format](http://lpsolve.sourceforge.net/5.0/CPLEX-format.htm) (option ```-milp```)

Optional arguments:
* ```-semiCont``` available with ```-milp``` for using [semi-continuous variables](http://lpsolve.sourceforge.net/5.5/semi-cont.htm) when possible

Examples:
```terminal
> ./src/pimc_modeler -smt -i data/pimcs/example.pimc -o /tmp/out.smt
> z3 -smt2  /tmp/out.smt

> ./src/pimc_modeler -milp -i data/pimcs/example.pimc -o /tmp/out.lp
> cplex -c 'read /tmp/out.lp lp' 'optimize' 'display solution variables -'
```

## References
[1] Delahaye, B., Lime, D., Petrucci, L.: Parameter synthesis for parametric interval markov chains. 
In: Verification, Model Checking, and Abstract Interpretation - 17th International Conference, VMCAI 2016, St. Petersburg, FL, USA, January 17-19, 2016. Proceedings. pp. 372–390 (2016)
