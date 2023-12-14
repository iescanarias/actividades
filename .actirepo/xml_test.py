import xml.etree.ElementTree as ET

xml = """
<quiz>
  <question type="truefalse">
    <name>
      <text>verdadero/falso</text>
    </name>
    <questiontext format="html">
      <text><![CDATA[<p>enunciado</p>]]></text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>1.0000000</defaultgrade>
    <penalty>1.0000000</penalty>
    <hidden>0</hidden>
    <idnumber></idnumber>
    <answer fraction="100" format="moodle_auto_format">
      <text>true</text>
      <feedback format="html">
        <text></text>
      </feedback>
    </answer>
    <answer fraction="0" format="moodle_auto_format">
      <text>false</text>
      <feedback format="html">
        <text></text>
      </feedback>
    </answer>
  </question>
</quiz>
"""

tree = ET.fromstring(xml)
questions = tree.findall('question')
for q in questions:
    print({
        "type": q.get('type'),
        "name": q.find('name').find('text').text,
        "questiontext": q.find('questiontext').find('text').text,
        "answers": [
            {
                "text": a.find('text').text,
                "feedback": a.find('feedback').find('text').text,
                "fraction": a.get('fraction')
            } for a in q.findall('answer')
        ]
    })
