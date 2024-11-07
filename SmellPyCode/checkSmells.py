from smells.AssertRouletteSmell import AssertRoulette
from smells.ConditionTestLogicSmell import ConditionTestLogic
from smells.ConstructorInitializationSmell import ConstructorInitialization
from smells.DefaultTestSmell import DefaultTest
from smells.DuplicateAssertSmell import DuplicateAssert
from smells.EagerTestSmell import EagerTest
from smells.EmptyTestSmell import EmptyTest
from smells.ExceptionHandlingSmell import ExceptionHandling
from smells.FixtureAsssertSmell import FixtureAssert
from smells.GeneralFixtureSmell import GeneralFixture
from smells.IgnoredTestSmell import IgnoredTest
from smells.MagicNumberSmell import MagicNumber
from smells.MysteryGuestSmell import MysteryGuest
from smells.ObscureInLineSetupSmell import ObscureInlineSetup
from smells.RedundantAssertSmell import RedundantAssert
from smells.RedundantPrintSmell import RedundantPrint
from smells.ResourceOptimismSmell import ResourceOptimism
from smells.SleepyTestSmell import SleepyTest
from smells.SuboptimalAssertSmell import SuboptimalAssert
from smells.TestMaverickSmell import TestMaverick
from smells.UnknownTestSmell import UnknownTest

import ast
import astunparse
import glob, os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

test_folder = ''
result_dir = ''

def read_test_code(file_path):
    with open(file_path, 'r') as f:
        return f.read()

class ClearValueTransformer(ast.NodeTransformer):
    def visit_Assign(self, node):
        # Clear value for specific assignments (e.g., mock_task.loop = 'foo')
        if isinstance(node.value, ast.Str) and any(isinstance(target, ast.Attribute) for target in node.targets):
            node.value = ast.Str(s='')
        return node

    def visit_Call(self, node):
        # Clear arguments for function calls
        if isinstance(node.func, ast.Attribute) or isinstance(node.func, ast.Name):
            node.args = [ast.Str(s='')]
        return node

def is_setup_function(node):
    # Check if it's a function definition
    if isinstance(node, ast.FunctionDef):
        # Check for unittest's setUp or setUpClass methods
        if node.name in ('setUp', 'setUpClass', '__init__'):
            return True
        # Check for pytest fixtures
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'pytest.fixture':
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'fixture':
                return True
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'fixture':
                return True
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'fixture':
                return True
    return False

def is_test_function(node):
    return isinstance(node, ast.FunctionDef) and (node.name.startswith('test_') or node.name.endswith('_test'))

def get_setup_functions(test_class_node):
    return [node for node in test_class_node.body if is_setup_function(node)]

def get_test_functions(test_class_node):
    return [node for node in test_class_node.body if is_test_function(node)]

def recreate_test_class(test_class_node, setup_functions, test_function, imports):
    return astunparse.unparse(ast.Module(imports + [
        ast.ClassDef(
            name=test_class_node.name,
            bases=test_class_node.bases,
            keywords=[],
            body=setup_functions + [test_function],
            decorator_list=[]
        )
    ]))


def recreate_test_function(test_function_node, imports, setup_function_nodes):
    return astunparse.unparse(ast.Module(imports + setup_function_nodes + [
        ast.FunctionDef(
            name=test_function_node.name,
            args=test_function_node.args,
            body=test_function_node.body,
            decorator_list=test_function_node.decorator_list,
            returns=test_function_node.returns
        )
    ]))

def get_imports(module):
    return [node for node in module.body if isinstance(node, (ast.Import, ast.ImportFrom))]

def detect_smells(test_code):
    detectors = [
        AssertRoulette, ConditionTestLogic, ConstructorInitialization, DefaultTest, DuplicateAssert,
        EagerTest, EmptyTest, ExceptionHandling, FixtureAssert, GeneralFixture, IgnoredTest, MagicNumber,
        MysteryGuest, ObscureInlineSetup, RedundantAssert, RedundantPrint, ResourceOptimism,
        SleepyTest, SuboptimalAssert, TestMaverick, UnknownTest
    ]
    # init a dictionary to store the result
    result = {}
    for Detector in detectors:
        detector = Detector(test_code)
        # print(f"has {Detector.__name__.lower()} smell: ", detector.detect_smell())
        try:
            if detector.detect_smell():
                result[Detector.__name__.lower()] = detector.detect_smell()
        except:
            print(f"failed to detect {Detector.__name__.lower()}")
            pass
    return result


def detect_functions_similarity(test_function_nodes):
    try:
        test_function_names = []
        test_functions = []
        transformer = ClearValueTransformer()
        for test_function_node in test_function_nodes:
            if 'test' in test_function_node.name:
                transformed_ast = transformer.visit(test_function_node)
                ast.fix_missing_locations(transformed_ast)
                function_string = astunparse.unparse(ast.FunctionDef(
                    name='',
                    args=[],
                    body=test_function_node.body,
                    decorator_list=[],
                    returns=test_function_node.returns)).replace('\n', ' ')
                # further remove

                test_functions.append(function_string)
                test_function_names.append(test_function_node.name)
        # Vectorize the function texts
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(test_functions)

        # Calculate cosine similarity
        cos_similarity_matrix = cosine_similarity(tfidf_matrix)

        # Initialize a list to store pairs of similar functions
        similar_functions_pairs = []

        # Iterate over the matrix to find function pairs with similarity > 0.8
        for i in range(len(cos_similarity_matrix)):
            for j in range(i + 1, len(cos_similarity_matrix)):  # Compare each pair once
                if cos_similarity_matrix[i, j] > 0.85:
                    # Save the pair of indices or the actual functions
                    similar_functions_pairs.append((test_function_names[i], test_function_names[j]))
    except:
        similar_functions_pairs = []
    # Return the list of similar function pairs
    return similar_functions_pairs


def main():
    detectors = [
        AssertRoulette, ConditionTestLogic, ConstructorInitialization, DefaultTest, DuplicateAssert,
        EagerTest, EmptyTest, ExceptionHandling, FixtureAssert, GeneralFixture, IgnoredTest, MagicNumber,
        MysteryGuest, ObscureInlineSetup, RedundantAssert, RedundantPrint, ResourceOptimism,
        SleepyTest, SuboptimalAssert, TestMaverick, UnknownTest
    ]
    by_smell = {}
    for Detector in detectors:
        by_smell[Detector.__name__.lower()] = []
    test_method_count = 0
    smell_count = 0
    # literate through all test files in the test_folder
    for root, dirs, files in os.walk(test_folder):
        for file in glob.glob(root+'/*.py'):
            try:
                if 'test' not in file.split('/')[-1]:
                    continue
                with open(file, 'r') as f:
                    module = ast.parse(f.read())
                imports = get_imports(module)
                class_nodes = [node for node in module.body if isinstance(node, ast.ClassDef)]

                for class_node in class_nodes:
                    setup_functions = get_setup_functions(class_node)
                    test_functions = get_test_functions(class_node)
                    for test_function in test_functions:
                        try:
                            if 'test' not in test_function.name:
                                continue

                            print("\n\ntest function: ", test_function.name)

                            test_method_count += 1
                            test_class_code = recreate_test_class(class_node, setup_functions, test_function, imports)

                            tempResult = detect_smells(test_class_code)
                            if len(tempResult) > 0:
                                # save to by_smell
                                for key, value in tempResult.items():
                                    by_smell[key].append(file.split('/')[-1] + ' ::: ' + class_node.name + ' ::: ' + test_function.name)
                                print(tempResult)
                                smell_count += 1

                        except Exception as e:
                            print('error1: ', e)
                            continue
                    similar_list = detect_functions_similarity(test_functions)

                    if len(similar_list) > 0:
                        with open(result_dir + '/' + file.split('/')[-1].replace('.py', '') + '.txt', 'a+') as f:
                            f.write('similar functions: \n')
                            for pair in similar_list:
                                f.write(pair[0] + ' ' + pair[1] + '\n')
                            f.write('\n')

                # if len(class_nodes) == 0:
                tmp_function_nodes = [node for node in module.body if isinstance(node, ast.FunctionDef)]
                function_nodes = []
                setup_functions = []
                #check if the function is a test function or a setup function
                for function_node in tmp_function_nodes:
                    if is_setup_function(function_node):
                        setup_functions.append(function_node)
                    elif is_test_function(function_node):
                        function_nodes.append(function_node)


                for function_node in function_nodes:
                    try:
                        if 'test' not in function_node.name:
                            continue
                        print("\n\ntest function: ", function_node.name)
                        test_method_count += 1
                        test_function_node = recreate_test_function(function_node, imports, setup_functions)
                        tempResult = detect_smells(test_function_node)
                        if len(tempResult) > 0:
                            # save to by_smell
                            for key, value in tempResult.items():
                                by_smell[key].append(file.split('/')[-1] + ' ' + function_node.name)
                            smell_count += 1

                    except Exception as e:
                        print('error2: ', e)
                        continue
                similar_list = detect_functions_similarity(function_nodes)
                if len(similar_list) > 0:
                    with open(result_dir + '/' + file.split('/')[-1].replace('.py', '') + '.txt', 'a+') as f:
                        f.write('similar functions: \n')
                        for pair in similar_list:
                            f.write(pair[0] + ' ' + pair[1] + '\n')
                        f.write('\n')

            except Exception as e:
                print('error3: ', e)
                continue
    print("test method count: ", test_method_count)
    print("smell count: ", smell_count)

    for key, value in by_smell.items():
        # save to a local file
        if not os.path.exists(result_dir + '/bySmell'):
            os.makedirs(result_dir + '/bySmell')
        with open(result_dir + '/bySmell/' + key + '.txt', 'w') as f:
            for item in value:
                f.write("%s\n" % item)

if __name__ == "__main__":
    main()
