
import test_appliance

from yaml import *

class TestStructure(test_appliance.TestAppliance):

    def _testStructure(self, test_name, data_filename, structure_filename):
        node1 = None
        node2 = eval(file(structure_filename, 'rb').read())
        try:
            parser = Parser(Scanner(Reader(file(data_filename, 'rb'))))
            node1 = []
            while not parser.check(StreamEndEvent):
                node1.append(self._convert(parser))
            parser.get()
            if len(node1) == 1:
                node1 = node1[0]
            self.failUnlessEqual(node1, node2)
        except:
            print
            print "DATA:"
            print file(data_filename, 'rb').read()
            print "NODE1:", node1
            print "NODE2:", node2
            raise

    def _convert(self, parser):
        if parser.check(ScalarEvent):
            event = parser.get()
            if event.tag or event.anchor or event.value:
                return True
            else:
                return None
        elif parser.check(SequenceEvent):
            parser.get()
            sequence = []
            while not parser.check(CollectionEndEvent):
                sequence.append(self._convert(parser))
            parser.get()
            return sequence
        elif parser.check(MappingEvent):
            parser.get()
            mapping = []
            while not parser.check(CollectionEndEvent):
                key = self._convert(parser)
                value = self._convert(parser)
                mapping.append((key, value))
            parser.get()
            return mapping
        elif parser.check(AliasEvent):
            parser.get()
            return '*'
        else:
            parser.get()
            return '?'

TestStructure.add_tests('testStructure', '.data', '.structure')

class TestParser(test_appliance.TestAppliance):

    def _testParser(self, test_name, data_filename, canonical_filename):
        events1 = None
        events2 = None
        try:
            parser = Parser(Scanner(Reader(file(data_filename, 'rb'))))
            events1 = list(iter(parser))
            canonical = test_appliance.CanonicalParser(file(canonical_filename, 'rb').read())
            events2 = canonical.parse()
            self._compare(events1, events2)
        except:
            print
            print "DATA1:"
            print file(data_filename, 'rb').read()
            print "DATA2:"
            print file(canonical_filename, 'rb').read()
            print "EVENTS1:", events1
            print "EVENTS2:", events2
            raise

    def _compare(self, events1, events2):
        self.failUnlessEqual(len(events1), len(events2))
        for event1, event2 in zip(events1, events2):
            self.failUnlessEqual(event1.__class__, event2.__class__)
            if isinstance(event1, AliasEvent):
                #self.failUnlessEqual(event1.name, event2.name)
                pass
            elif isinstance(event1, ScalarEvent):
                #self.failUnlessEqual(event1.anchor, event2.anchor)
                #self.failUnlessEqual(event1.tag, event2.tag)
                self.failUnlessEqual(event1.value, event2.value)
            if isinstance(event1, CollectionEvent):
                #self.failUnlessEqual(event1.anchor, event2.anchor)
                #self.failUnlessEqual(event1.tag, event2.tag)
                pass

TestParser.add_tests('testParser', '.data', '.canonical')

class TestResolver(test_appliance.TestAppliance):

    def _testResolver(self, test_name, data_filename, canonical_filename):
        nodes1 = None
        nodes2 = None
        try:
            resolver1 = Resolver(Composer(Parser(Scanner(Reader(file(data_filename, 'rb'))))))
            nodes1 = list(iter(resolver1))
            canonical = test_appliance.CanonicalParser(file(canonical_filename, 'rb').read())
            canonical.parse()
            resolver2 = Resolver(Composer(canonical))
            nodes2 = list(iter(resolver2))
            self.failUnlessEqual(len(nodes1), len(nodes2))
            for node1, node2 in zip(nodes1, nodes2):
                self._compare(node1, node2)
        except:
            print
            print "DATA1:"
            print file(data_filename, 'rb').read()
            print "DATA2:"
            print file(canonical_filename, 'rb').read()
            print "NODES1:", nodes1
            print "NODES2:", nodes2
            raise

    def _compare(self, node1, node2):
        self.failUnlessEqual(node1.__class__, node2.__class__)
        if isinstance(node1, ScalarNode):
            #self.failUnlessEqual(node1.tag, node2.tag)
            self.failUnlessEqual(node1.value, node2.value)
        elif isinstance(node1, SequenceNode):
            self.failUnlessEqual(len(node1.value), len(node2.value))
            for item1, item2 in zip(node1.value, node2.value):
                self._compare(item1, item2)
        elif isinstance(node1, MappingNode):
            self.failUnlessEqual(len(node1.value), len(node2.value))
            items1 = node1.value.items()
            items1.sort(lambda (k1,v1), (k2,v2): cmp((k1.tag,k1.value,v1.tag,v1.value),
                                                    (k2.tag,k2.value,v2.tag,v2.value)))
            items2 = node2.value.items()
            items2.sort(lambda (k1,v1), (k2,v2): cmp((k1.tag,k1.value,v1.tag,v1.value),
                                                    (k2.tag,k2.value,v2.tag,v2.value)))
            for (key1, value1), (key2, value2) in zip(items1, items2):
                self._compare(key1, key2)
                self._compare(value1, value2)

TestResolver.add_tests('testResolver', '.data', '.canonical')

class MyConstructor(Constructor):

    def construct_sequence(self, node):
        return tuple(Constructor.construct_sequence(self, node))

    def construct_mapping(self, node):
        pairs = self.construct_pairs(node)
        pairs.sort()
        return pairs

MyConstructor.add_constructor(None, MyConstructor.construct_scalar)

class TestConstructor(test_appliance.TestAppliance):

    def _testConstructor(self, test_name, data_filename, canonical_filename):
        natives1 = None
        natives2 = None
        try:
            constructor1 = MyConstructor(Resolver(Composer(Parser(Scanner(Reader(file(data_filename, 'rb')))))))
            natives1 = list(iter(constructor1))
            canonical = test_appliance.CanonicalParser(file(canonical_filename, 'rb').read())
            canonical.parse()
            constructor2 = MyConstructor(Resolver(Composer(canonical)))
            natives2 = list(iter(constructor2))
            self.failUnlessEqual(natives1, natives2)
        except:
            print
            print "DATA1:"
            print file(data_filename, 'rb').read()
            print "DATA2:"
            print file(canonical_filename, 'rb').read()
            print "NATIVES1:", natives1
            print "NATIVES2:", natives2
            raise

TestConstructor.add_tests('testConstructor', '.data', '.canonical')

class TestParserOnCanonical(test_appliance.TestAppliance):

    def _testParserOnCanonical(self, test_name, canonical_filename):
        events1 = None
        events2 = None
        try:
            parser = Parser(Scanner(Reader(file(canonical_filename, 'rb'))))
            events1 = list(iter(parser))
            canonical = test_appliance.CanonicalParser(file(canonical_filename, 'rb').read())
            events2 = canonical.parse()
            self._compare(events1, events2)
        except:
            print
            print "DATA:"
            print file(canonical_filename, 'rb').read()
            print "EVENTS1:", events1
            print "EVENTS2:", events2
            raise

    def _compare(self, events1, events2):
        self.failUnlessEqual(len(events1), len(events2))
        for event1, event2 in zip(events1, events2):
            self.failUnlessEqual(event1.__class__, event2.__class__)
            if isinstance(event1, AliasEvent):
                self.failUnlessEqual(event1.anchor, event2.anchor)
            elif isinstance(event1, ScalarEvent):
                self.failUnlessEqual(event1.anchor, event2.anchor)
                self.failUnlessEqual(event1.tag, event2.tag)
                self.failUnlessEqual(event1.value, event2.value)
            if isinstance(event1, CollectionEvent):
                self.failUnlessEqual(event1.anchor, event2.anchor)
                self.failUnlessEqual(event1.tag, event2.tag)

TestParserOnCanonical.add_tests('testParserOnCanonical', '.canonical')
