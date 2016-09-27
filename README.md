# pimc_pylib
Python library for Parametric Interval Markov Chains (PIMC) manipulation.
This library allows to: 
* generate PIMCs from MCs (see. Section PIMC generator)
* generate CSP models for PIMC verification (see. Section PIMC modeler)

## PIMC generator
The PIMC generator transform a Discrete Time Markov Chain (MC for short) to a Parametric Interval Markov Chains. The scrip takes one configuration file as argument. The configuration must be written in the JSON format. It contains the location file of the MC to consider and how many parameters and intervals must be added from the MC to generate a PIMC. The MC file must written in the [PRISM language](http://www.prismmodelchecker.org/). In order to generate a PIMC, the 4 following values must be set in the generator configuration input file:
- location of the PRISM model (key: ```prismFile```)
- the constants in the PRISM model associated with a value (key: ```prismConstants```)
- the number of parameters to insert in the PIMC (key: ```nbParameters```)
- the ratio value for the number of intervals over the number of transitions in PIMC (key: ```ratioIntervals```)
- the ratio value for the number of parameters over the number of interval endpoints in the PIMC (key: ```ratioParameters```)

The values associated to the keys can be either one value or a list of values. In the case of a list of values, the PIMC generator will consider all the possible combinaisons of values between all the keys. Some examples of configuration files for PIMC generation cand be found in [data/generator/config](https://github.com/anicet-bart/pimc_pylib/tree/master/data/generator). Some examples of PRISM files can be found in [data/generator/inputs](https://github.com/anicet-bart/pimc_pylib/tree/master/data/generator/inputs) (from [PRISM benchmarks](http://www.prismmodelchecker.org/benchmarks/models.php#dtmcs)).

Example 1: the following configuration file will generate one PIMC:
```json
{
	"prismFile"     : "data/generator/inputs/brp.pm",
	"prismConstants": 
	{
		"N" : 16,
		"MAX" : 3
	},
	"nbParameters"   : 5,
	"ratioIntervals" : 0.2,
	"ratioParameters": 0.1
}
```

Example 2: the following configuration file will generate 16 PIMCs:
```json
{
	"prismFile"     : "data/generator/inputs/brp.pm",
	"prismConstants": 
	{
		"N" : [16, 32],
		"MAX" : [3, 4]
	},
	"nbParameters"   : [2, 5], 
	"ratioIntervals" : 0.2,
	"ratioParameters": [0.05, 0.1]
}
```



Warning: the library needs to call PRISM. Do not forget to set the location of your PRISM directory in the configuration file config.ini

## PIMC modeler
