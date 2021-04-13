import argparse
import pathlib
import sys
from ply.yacc import yacc
from uc.uc_lexer import UCLexer


class UCParser:
    def __init__(self, debug=True):
        """Create a new uCParser."""
        self.uclex = UCLexer(self._lexer_error)
        self.uclex.build()
        self.tokens = self.uclex.tokens

        self.ucparser = yacc(module=self, start="program", debug=debug)
        # Keeps track of the last token given to yacc (the lookahead token)
        self._last_yielded_token = None

    def show_parser_tree(self, text):
        print(self.parse(text))

    def parse(self, text, debuglevel=0):
        self.uclex.reset_lineno()
        self._last_yielded_token = None
        return self.ucparser.parse(input=text, lexer=self.uclex, debug=debuglevel)

    def _lexer_error(self, msg, line, column):
        # use stderr to match with the output in the .out test files
        print("LexerError: %s at %d:%d" % (msg, line, column), file=sys.stderr)
        sys.exit(1)

    def _parser_error(self, msg, line="", column=""):
        # use stderr to match with the output in the .out test files
        if line == "" and column == "":
            print("ParserError: %s" % (msg), file=sys.stderr)
        if column == "":
            print("ParserError: %s at %s" % (msg, line), file=sys.stderr)
        else:
            print("ParserError: %s at %s:%s" % (msg, line, column), file=sys.stderr)
        sys.exit(1)
        
    precedence = (
        ('left', 'AND', 'OR'),
        ('nonassoc', 'EQ', 'NE'),
        ('nonassoc', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD'),
        ('nonassoc', 'INIT_DECLARATOR'),
        ('nonassoc', 'AFTER_DECL','PRIMARY'),
    )

    def p_program(self,p):
        ''' program : global_declaration_list
        '''
        p[0] = ('program', p[1])
        
    def p_global_declaration_list(self, p):
        ''' global_declaration_list : global_declaration_list global_declaration
                                    | global_declaration
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + (p[2])
    
    def p_global_declaration(self, p):
        ''' global_declaration : function_definition
                               | declaration
        '''
        p[0] = p[1]

    def p_function_definition(self, p):
        ''' function_definition : type_specifier declarator declaration_oplist compound_statement
        '''
        p[0] = (p[2], p[4])
        
    def p_type_specifier(self, p):
        ''' type_specifier : VOID
                           | CHAR
                           | INT
        '''
        p[0] = p[1]
        
    def p_declarator(self, p):
        ''' declarator : identifier %prec INIT_DECLARATOR
                       | LPAREN declarator RPAREN %prec AFTER_DECL
                       | declarator LBRACKET constant_expression_op RBRACKET %prec AFTER_DECL
                       | declarator LPAREN parameter_oplist RPAREN %prec AFTER_DECL
        '''
        if len(p) == 2:
            p[0] = p[1]
        elif(len(p) == 3):
            p[0] = p[2]
        else:
            p[0] = (p[1], p[3])
            
    def p_constant_expression_op(self, p):
        ''' constant_expression_op : constant_expression
                                   | empty
        '''
        p[0] = p[1]
        
    def p_constant_expression(self, p):
        ''' constant_expression : binary_expression
        '''
        p[0] = p[1]
    
    def p_parameter_oplist(self, p):
        ''' parameter_oplist : parameter_list
                              | empty
        '''
        p[0] = p[1]
    
    def p_parameter_list(self, p):
        ''' parameter_list : parameter_declaration
                           | parameter_list COMMA parameter_declaration
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[3])
            
    def p_parameter_declaration(self, p):
        ''' parameter_declaration : type_specifier declarator
        '''
        p[0] = p[2]        

    def p_statement(self,p):
        ''' statement : expression_statement
                      | compound_statement
                      | selection_statement
                      | iteration_statement
                      | jump_statement
                      | assert_statement
                      | print_statement
                      | read_statement
        '''
        p[0] = p[1]

    def p_expression_statement(self,p):
        ''' expression_statement : expression_op SEMI
        '''
        p[0] = p[1]
    
    def p_compound_statement(self, p):
        ''' compound_statement : LBRACE declaration_oplist statement_oplist RBRACE
        '''
        p[0] = (p[2],p[3])
        
    def p_selection_statement(self,p):
        ''' selection_statement : IF LPAREN expression RPAREN statement
                                | IF LPAREN expression RPAREN statement ELSE statement
        '''
        #vai dar conflito shift/reduce
        if len(p) == 6:
            p[0] = (p[1],p[3],p[5]) 
        else:
            p[0] = (p[1], p[3], p[5], p[6], p[7])
    
    def p_iteration_statement(self, p):
        ''' iteration_statement : WHILE LPAREN expression RPAREN statement
                                | FOR LPAREN expression_op SEMI expression_op SEMI expression_op RPAREN statement
                                | FOR LPAREN declaration expression_op SEMI expression_op RPAREN statement
        '''
        if len(p) == 6:
            p[0] = (p[1], p[3], p[5])
        elif(len(p) == 10):
            p[0] = (p[1], p[3],p[5],p[7],p[9])
        else:
            p[0] = (p[1], p[3], p[4], p[6], p[8])
            
    def p_jump_statement(self, p):
        ''' jump_statement : BREAK SEMI
                           | RETURN expression_op SEMI
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[2])
            
    def p_assert_statement(self, p):
        ''' assert_statement : ASSERT expression SEMI
        '''
        p[0] = (p[1], p[2])
        
    def p_print_statement(self, p):
        ''' print_statement : PRINT LPAREN expression_op  RPAREN SEMI
        '''
        p[0] = (p[1], p[3])
        
    def p_read_statement(self, p):
        ''' read_statement : READ LPAREN argument_expression RPAREN SEMI
        '''
        p[0] = (p[1], p[3])
        
    def p_declaration_oplist(self, p):
        ''' declaration_oplist : declaration_oplist declaration
                               | empty
        '''
        if len(p) == 2:
            p[0] = ()
        else:
            p[0] = p[1] + p[2]
            
    def p_declaration(self, p):
        ''' declaration : type_specifier init_declarator_list_op SEMI
        '''
        p[0] = (p[1], p[2])
    
    def p_init_declarator_list_op(self, p):
        ''' init_declarator_list_op : init_declarator_list
                                    | empty
        '''
        p[0] = p[1]
        
    def p_init_declarator_list(self, p):
        ''' init_declarator_list : init_declarator
                                 | init_declarator_list COMMA init_declarator
        '''
        if len(p) == 2:
            p[0] = p[1]
        else: 
            p[0] = (p[1], p[3])
    
    def p_init_declarator(self, p):
        ''' init_declarator : declarator %prec INIT_DECLARATOR
                            | declarator EQUALS initializer %prec AFTER_DECL
        '''
        if len(p) == 2:
            p[0] = p[1]
        else: 
            p[0] = (p[1], p[3])
            
    def p_initializer(self, p):
        ''' initializer : assignment_expression
                        | LBRACE initializer_list_op RBRACE
                        | LBRACE initializer_list COMMA RBRACE
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]
        
    def p_initializer_list_op(self, p):
        ''' initializer_list_op : initializer_list
                                | empty
        '''
        p[0] = p[1]
    
    def p_initializer_list(self, p):
        ''' initializer_list : initializer
                             | initializer_list COMMA initializer
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[3])
        
    def p_statement_oplist(self, p):
        ''' statement_oplist : statement_oplist statement
                             | empty
        '''
        if len(p) == 2:
            p[0] = ()
        else:
            p[0] = p[1] + p[2]

    def p_expression_op(self,p):
        ''' expression_op : expression 
                          | empty
        '''
        p[0] = p[1]
        
    def p_expression(self, p):
        ''' expression : assignment_expression
                       | expression COMMA assignment_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[2], p[3])
            
    def p_assignment_expression(self, p):
        ''' assignment_expression : binary_expression
                                   | unary_expression EQUALS binary_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ('assign', p[1], p[3])
    
    def p_binary_expression(self, p):
        ''' binary_expression : unary_expression
                              | binary_expression TIMES binary_expression
                              | binary_expression DIVIDE binary_expression
                              | binary_expression MOD binary_expression
                              | binary_expression PLUS binary_expression
                              | binary_expression MINUS binary_expression
                              | binary_expression LT binary_expression
                              | binary_expression LE binary_expression
                              | binary_expression GT binary_expression
                              | binary_expression GE binary_expression
                              | binary_expression EQ binary_expression
                              | binary_expression NE binary_expression
                              | binary_expression AND binary_expression
                              | binary_expression OR binary_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[2], p[1], p[3]) 
        pass

    def p_unary_expression(self, p):
        ''' unary_expression : postfix_expression
                             | unary_operator unary_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[2])
    
    def p_unary_operator(self, p):
        ''' unary_operator : PLUS
                           | MINUS
                           | NOT
        '''
        p[0] = p[1]
    
    def p_postfix_expression(self, p):
        ''' postfix_expression : primary_expression
                               | postfix_expression LBRACKET expression RBRACKET
                               | postfix_expression LPAREN argument_expression_op RPAREN
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[3]) 
    
    def p_argument_expression_op(self, p):
        ''' argument_expression_op : argument_expression
                                   | empty
        '''
        p[0] = p[1]
    
    def p_argument_expression(self, p):
        ''' argument_expression : assignment_expression
                                | argument_expression COMMA assignment_expression
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1],p[2])

    def p_primary_expression(self, p):
        ''' primary_expression : identifier %prec PRIMARY
                               | constant 
                               | string
                               | LPAREN expression RPAREN
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_identifier(self, p):
        '''identifier : ID '''
        p[0] = p[1]
    
    def p_constant(self, p):
        ''' constant : INT_CONST
                     | CHAR_CONST
        '''
        p[0] = p[1]

    def p_string(self, p):
        '''string : STRING_LITERAL
        '''
        p[0] = p[1]

    def p_empty(self, p):
        '''empty : '''
        pass

    def p_error(self,p):
        if p:
            self._parser_error(
                "Before: %s" % p.value, p.lineno, self.uclex.find_tok_column(p)
            )
        else:
            self._parser_error("At the end of input (%s)" % self.uclex.filename)

            

if __name__ == "__main__":

    # create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to file to be parsed", type=str)
    args = parser.parse_args()

    # get input path
    input_file = args.input_file
    input_path = pathlib.Path(input_file)

    # check if file exists
    if not input_path.exists():
        print("Input", input_path, "not found", file=sys.stderr)
        sys.exit(1)

    # set error function
    p = UCParser()

    # open file and print tokens
    with open(input_path) as f:
        # p.parse(f.read())
        # use show_parser_tree instead of parser to print it
        p.show_parser_tree(f.read())
