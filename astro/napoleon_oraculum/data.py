from __future__ import annotations

from typing import Any

questions = [
    "Shall I obtain my wish?",
    "Shall I have success in my undertakings?",
    "Shall I gain or lose in my cause?",
    "Shall I have to live in foreign parts?",
    "Will the Stranger return from abroad?",
    "Shall I recover my property stolen?",
    "Will my friend be true in his dealings?",
    "Shall I have to travel?",
    "Does the person love and regard me?",
    "Will the marriage be prosperous?",
    "What sort of a wife or husband shall I have?",
    "Will she have a son or a daughter?",
    "Will the Patient recover from his illness?",
    "Will the Prisoner be released?",
    "Shall I be lucky or unlucky this day?",
    "What does my dream signify?",
]

questions_zh = [
    "我能如願以償嗎？",
    "我的事業與計畫會成功嗎？",
    "我的這件事情會得利還是失利？",
    "我會在異鄉生活嗎？",
    "那位遠行者會從海外歸來嗎？",
    "我能找回被盜的財物嗎？",
    "我的朋友在往來中會真誠可靠嗎？",
    "我將要出行旅行嗎？",
    "那個人愛我、重視我嗎？",
    "這段婚姻會幸福順遂嗎？",
    "我會有怎樣的妻子或丈夫？",
    "她會生兒子還是女兒？",
    "病人會從這場病中康復嗎？",
    "囚犯會被釋放嗎？",
    "我今天是幸運還是不幸？",
    "我的夢象徵著什麼？",
]

question_pairs = [
    {"en": en, "zh": zh}
    for en, zh in zip(questions, questions_zh)
]

oraculum = [
    ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q"],
    ["B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "Ɐ"],
    ["C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B"],
    ["D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C"],
    ["E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D"],
    ["F", "G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E"],
    ["G", "H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F"],
    ["H", "I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G"],
    ["I", "K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H"],
    ["K", "L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I"],
    ["L", "M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K"],
    ["M", "N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L"],
    ["N", "O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M"],
    ["O", "P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N"],
    ["P", "Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O"],
    ["Q", "A", "B", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "O", "P"],
]

answers = {'A': ['What you wish for, you will shortly OBTAIN.', 'Signifies trouble and sorrow.', 'Be very cautious what you do THIS day, lest trouble befall you.', 'The prisoner DIES, and is regretted by his friends.', 'Life will be spared THIS time, to prepare for death.', 'A very handsome daughter, but a PAINFUL one.', 'You will have a virtuous woman or man, for your wife or husband.', 'If you marry this person, you will have enemies where you little expect.', 'You had better decline THIS love, for it is neither constant nor true.', 'Decline your travels, for they will not be to your advantage.', 'There is a true and sincere friendship between you BOTH.', 'You will NOT recover the stolen property.', 'The stranger WILL, with joy, soon return.', 'You will NOT remove from where you are at present.', 'Providence WILL support you in a good cause.', 'You are NOT lucky.'], 'B': ['The luck that is ordained for you will be coveted by others.', 'Whatever your desires are, for the present decline them.', 'Signifies a favor or kindness from some person.', 'There ARE enemies who would defraud and render you unhappy.', 'With great difficulty he will obtain pardon or release again.', 'The patient should be prepared to LEAVE this world.', 'She will have a SON, who will be learned and wise.', 'A RICH partner is ordained for you.', 'By THIS marriage you will have great luck and prosperity.', 'This love comes from an upright and sincere heart.', 'A higher Power WILL surely travel with you, and bless you.', 'Beware of friends who are false and deceitful.', 'You WILL recover your property—unexpectedly.', 'Love prevents his return home at present.', 'Your stay is NOT here; be therefore prepared for a change.', 'You will have NO GAIN; therefore be wise and careful.'], 'C': ['With the blessing of God, you WILL have great gain.', 'Very unlucky indeed—pray for assistance.', 'If your desires are NOT extravagant, they will be granted.', 'Signifies peace and plenty between friends.', 'Be well prepared THIS day, or you may meet with trouble.', 'The prisoner WILL find it difficult to obtain his pardon or release.', 'The patient WILL YET enjoy health and prosperity.', 'She WILL have a daughter, and will require attention.', 'The person has NOT a great fortune, but is in middling circumstances.', 'Decline THIS marriage, or else you may be sorry.', 'Decline a courtship which MAY be your destruction.', 'Your travels are IN VAIN; you had better stay at home.', 'You MAY depend on a true and sincere friendship.', 'You must NOT expect to regain that which you have lost.', 'Sickness prevents the traveler from seeing you.', 'It WILL be your fate to stay where you now are.'], 'D': ['You WILL obtain a great fortune in another country.', 'By venturing freely, you WILL certainly gain doubly.', 'A higher Power WILL change your misfortune into success and happiness.', 'Alter your intentions, or else you MAY meet poverty and distress.', 'Signifies you have many impediments in accomplishing your pursuits.', 'Whatever may possess your inclinations this day, abandon them.', 'The prisoner WILL get free again this time.', 'The patient’s illness WILL be lingering and doubtful.', 'She will have a dutiful and handsome son.', 'The person will be LOW in circumstances, but honest-hearted.', 'A marriage which WILL ADD to your welfare and prosperity.', 'You love a person who does not speak well of you.', 'Your travels WILL be prosperous, if guided by prudence.', 'He means NOT what he says, for his heart is false.', 'With some trouble and expense, you may regain your property.', 'You must NOT expect to see the stranger again.'], 'E': ['The stranger WILL not return as soon as you expect.', 'Remain among your friends, and you will do well.', 'You will hereafter GAIN what you seek.', 'You have NO LUCK—pray, and strive honestly.', 'You will obtain your wishes by means of a friend.', 'Signifies you have enemies who will endeavor to ruin you.', 'Beware—an enemy is endeavoring to bring you to strife and misfortune.', 'The prisoner’s sorrow and anxiety are great, and his release uncertain.', 'The patient WILL soon recover—there is no danger.', 'She will have a daughter, who will be honored and respected.', 'Your partner WILL be fond of liquor, and will debase himself thereby.', 'This marriage will bring you to poverty, be therefore discreet.', 'Their love is false to you, and true to others.', 'Decline your travels for the present, for they will be dangerous.', 'This person is serious and true, and deserves to be respected.', 'You will not recover the property you have lost.'], 'F': ['By persevering you WILL recover your property again.', 'It is out of the stranger’s power to return.', 'You will GAIN, and be successful in foreign parts.', 'A great fortune is ordained for you; wait patiently.', 'There is great hindrance to your success at present.', 'Your wishes are in VAIN at present.', 'Signifies there are sorrow and danger before you.', 'This day is unlucky; therefore alter your intention.', 'The prisoner will be restored to liberty and freedom.', 'The patient’s recovery is doubtful.', 'She will have a fine BOY.', 'A worthy person, and a fine fortune.', 'Your intentions would destroy your rest and peace.', 'This love is true and constant; forsake it not.', 'Proceed on your journey, and you will not have cause to repent it.', 'If you trust THIS friend, you may have cause for sorrow.'], 'G': ['This friend exceeds all others in every respect.', 'You must bear your loss with fortitude.', 'The stranger will return unexpectedly.', 'Remain at HOME with your friends, and you will escape misfortunes.', 'You will meet no GAIN in your pursuits.', 'Heaven will bestow its blessings on you.', 'No.', 'Signifies that you will shortly be out of the POWER of your enemies.', 'Ill-luck awaits you—it will be difficult for you to escape it.', 'The prisoner will be RELEASED by death only.', 'By the blessing of God, the patient WILL recover.', 'A daughter, but of a very sickly constitution.', 'You will get an honest, young, and handsome partner.', 'Decline this marriage, else it may be to your sorrow.', 'Avoid this love.', 'Prepare for a short journey; you will be recalled by unexpected events.'], 'H': ['Commence your travels, and they will go on as you could wish.', 'Your pretended friend hates you secretly.', 'Your hopes to recover your property are vain.', 'A certain affair prevents the stranger’s return immediately.', 'Your fortune you will find in abundance abroad.', 'Decline the pursuit, and you will do well.', 'Your expectations are vain—you will not succeed.', 'You will obtain what you wish for.', 'Signifies that on this day your fortune will change for the better.', 'Cheer up your spirits, your luck is at hand.', 'After LONG imprisonment, he will be released.', 'The patient will be relieved from sickness.', 'She will have a healthy SON.', 'You will be married to your equal in a short time.', 'If you wish to be happy, do not marry this person.', 'This love is from the heart, and will continue until death.'], 'I': ['The love is great, but will cause great jealousy.', 'It will be in vain for you to travel.', 'Your friend will be as sincere as you could wish him to be.', 'You will recover the stolen property through a cunning person.', 'The traveler will soon return with joy.', 'You will not be prosperous or fortunate in foreign parts.', 'Place your trust in God, who is the disposer of happiness.', 'Your fortune will shortly be changed into misfortune.', 'You will succeed as you desire.', 'Signifies that the misfortune which threatens will be prevented.', 'Beware of your enemies, who seek to do you harm.', 'After a short time, your anxiety for the prisoner will cease.', 'God will give the patient health and strength again.', 'She will have a very fine daughter.', 'You will marry a person with whom you will have little comfort.', 'The marriage will not answer your expectations.'], 'K': ['After much misfortune, you will be comfortable and happy.', 'A sincere love from an upright heart.', 'You will be prosperous in your journey.', 'Do not RELY on the friendship of this person.', 'The property is lost for EVER; but the thief will be punished.', 'The traveler will be absent some considerable time.', 'You will meet luck and happiness in a foreign country.', 'You will not have any success for the present.', 'You will succeed in your undertaking.', 'Change your intentions, and you will do well.', 'Signifies that there are rogues at hand.', 'Be reconciled, your circumstances will shortly mend.', 'The prisoner will be released.', 'The patient will depart this life.', 'She will have a son.', 'It will be difficult for you to get a partner.'], 'L': ['You will get a very handsome person for your partner.', 'Various misfortunes will attend this marriage.', 'This love is whimsical and changeable.', 'You will be unlucky in your travels.', 'This person’s love is just and true. You may rely on it.', 'You will lose, but the thief will suffer most.', 'The stranger will soon return with plenty.', 'If you remain at home, you will have success.', 'Your gain will be trivial.', 'You will meet sorrow and trouble.', 'You will succeed according to your wishes.', 'Signifies that you will get money.', 'In spite of enemies, you will do well.', 'The prisoner will pass many days in confinement.', 'The patient will recover.', 'She will have a daughter.'], 'M': ['She will have a son, who will gain wealth and honor.', 'You will get a partner with great undertakings and much money.', 'The marriage will be prosperous.', 'She, or He, wishes to be yours this moment.', 'Your journey will prove to your advantage.', 'Place no great trust in that person.', 'You will find your property at a certain time.', 'The traveler’s return is rendered doubtful by his conduct.', 'You will succeed as you desire in foreign parts.', 'Expect no gain; it will be in vain.', 'You will have more LUCK than you expect.', 'Whatever your desires are, you will speedily obtain them.', 'Signifies you will be asked to a wedding.', 'You will have no occasion to complain of ill-luck.', 'Someone will pity and release the prisoner.', 'The patient’s recovery is unlikely.'], 'N': ['The patient will recover, but his days are short.', 'She will have a daughter.', 'You will marry into a very respectable family.', 'By this marriage you will gain nothing.', 'Await the time and you will find the love great.', 'Venture not from home.', 'This person is a sincere friend.', 'You will never recover the theft.', 'The stranger will return, but not quickly.', 'When abroad, keep from evil women or they will do you harm.', 'You will soon gain what you little expect.', 'You will have great success.', 'Rejoice ever at that which is ordained for you.', 'Signifies that sorrow will depart, and joy will return.', 'Your luck is in blossom; it will soon be at hand.', 'Death may end the imprisonment.'], 'O': ['The prisoner will be released with joy.', 'The patient’s recovery is doubtful.', 'She will have a son, who will live to a great age.', 'You will get a virtuous partner.', 'Delay not this marriage—you will meet much happiness.', 'None loves you better in this world.', 'You may proceed with confidence.', 'Not a friend, but a secret enemy.', 'You will soon recover what is stolen.', 'The stranger will not return again.', 'A foreign woman will greatly enhance your fortune.', 'You will be cheated out of your gain.', 'Your misfortunes will vanish and you will be happy.', 'Your hope is in vain—fortune shuns you at present.', 'That you will soon hear agreeable news.', 'There are misfortunes lurking about you.'], 'P': ['This day brings you an increase of happiness.', 'The prisoner will quit the power of his enemies.', 'The patient will recover and live long.', 'She will have two daughters.', 'A rich young person will be your partner.', 'Hasten your marriage—it will bring you much happiness.', 'The person loves you sincerely.', 'You will not prosper from home.', 'This friend is more valuable than gold.', 'You will NEVER receive your goods.', 'He is dangerously ill, and cannot yet return.', 'Depend upon your own industry, and remain at home.', 'Be joyful, for future prosperity is ordained for you.', 'Depend not too much on your good luck.', 'What you wish will be granted to you.', 'That you should be very careful this day, lest any accident befall you.'], 'Q': ['Signifies much joy and happiness between friends.', 'This day is not very lucky, but rather the reverse.', 'He will yet come to honor, although he now suffers.', 'Recovery is doubtful; therefore be prepared for the worst.', 'She will have a son who will prove forward.', 'A rich partner, but a bad temper.', 'By wedding this person you insure your happiness.', 'The person has great love for you, but wishes to conceal it.', 'You may proceed on your journey without fear.', 'Trust him not; he is inconstant and deceitful.', 'In a very singular manner you will recover your property.', 'The stranger will return very soon.', 'You will dwell abroad in comfort and happiness.', 'If you will deal fairly you will surely prosper.', 'You will yet live in splendor and plenty.', 'Make yourself contented with your PRESENT fortune.'], 'Ɐ': ['What you wish for, you will shortly OBTAIN.', 'Signifies trouble and sorrow.', 'Be very cautious what you do THIS day, lest trouble befall you.', 'The prisoner DIES, and is regretted by his friends.', 'Life will be spared THIS time, to prepare for death.', 'A very handsome daughter, but a PAINFUL one.', 'You will have a virtuous woman or man, for your wife or husband.', 'If you marry this person, you will have enemies where you little expect.', 'You had better decline THIS love, for it is neither constant nor true.', 'Decline your travels, for they will not be to your advantage.', 'There is a true and sincere friendship between you BOTH.', 'You will NOT recover the stolen property.', 'The stranger WILL, with joy, soon return.', 'You will NOT remove from where you are at present.', 'Providence WILL support you in a good cause.', 'You are NOT lucky.']}


def get_oraculum_answer(question_index: int, number_index: int) -> dict[str, Any]:
    """Resolve letter and answer by question index and 0-based number index."""
    if not (0 <= question_index < 16):
        raise ValueError("question_index must be in 0..15")
    if not (0 <= number_index < 16):
        raise ValueError("number_index must be in 0..15")

    letter = oraculum[question_index][number_index]
    letter_answers = answers.get(letter)
    if not letter_answers:
        raise KeyError(f"No answers table for letter: {letter}")

    return {
        "question_en": questions[question_index],
        "question_zh": questions_zh[question_index],
        "question_index": question_index,
        "number": number_index + 1,
        "letter": letter,
        "answer": letter_answers[number_index],
    }
