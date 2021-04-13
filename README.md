# GFG
Lexical and Syntactic analysis of a Context-Free Grammar used to study.


The objective of this project is to implement a lexer and a parser for the uC language.

# Requirements
Use Python 3.5 or a newer version.
Required pip packages:
 - ply
 
# Running
To test the lexer, do:
```ruby
python3 uc_lexer.py test.in 
```

To test the parser, do:
```ruby
python3 uc_parser.py test.in 
```

where test.in is just a file with some code in uC.

#Notes
- I used the uC BNF Grammar to write RegEx and define the grammar rules in the parser.
- The output of uc_lexer.py is a list of TOKENS the were recognized by the RegEx written, or an error indicating invalid characters in the grammar.
- The output of uc_parser.py is a parser tree and some warnings if exist, or an error if the test.in language does not match the rules.
- At the moment, on shift/reduce conflict exists on the rule if then else, but its solved using shift. So its not an error.
- I will build the correct parser tree in a few days. The main goal here is recognize the grammar, independently of the formart of AST.
