import edu.stanford.nlp.ie.util.RelationTriple;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.naturalli.NaturalLogicAnnotations;
import edu.stanford.nlp.util.CoreMap;

import java.util.Collection;
import java.util.Properties;

/**
 * A demo illustrating how to call the OpenIE system programmatically.
 */
public class OpenIEDemo {

    public static void main(String[] args) throws Exception {
        // Create the Stanford CoreNLP pipeline
        Properties props = new Properties();
        props.setProperty("annotators", "tokenize,pos,lemma,depparse,natlog,openie");
        props.put("openie.triple.all_nominals", "true");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

        // Annotate an example document.
        Annotation doc = new Annotation(
                "When the Bank of England announced last week that it would buy bonds in unlimited quantities in an effort to stabilize the market for U.K. government debt, economists agreed it was probably a necessary move to prevent a cataclysmic financial crisis. They also worried it could set a dangerous precedent. Central banks defend the financial stability of the nations in which they operate. In an era of highly leveraged and deeply interconnected markets, that means that they sometimes have to buy bonds or backstop lending to prevent a problem in one area from spiraling into a crisis that threatens the entire financial system.");
        pipeline.annotate(doc);

        // Loop over sentences in the document
        for (CoreMap sentence : doc.get(CoreAnnotations.SentencesAnnotation.class)) {
            // Get the OpenIE triples for the sentence
            Collection<RelationTriple> triples = sentence.get(NaturalLogicAnnotations.RelationTriplesAnnotation.class);
            // Print the triples
            // System.out.println(triples);
            for (RelationTriple triple : triples) {
                System.out.println(triple.confidence + "\t" +
                        triple.subjectLemmaGloss() + "\t" +
                        triple.relationLemmaGloss() + "\t" +
                        triple.objectLemmaGloss());
            }
        }
    }
}