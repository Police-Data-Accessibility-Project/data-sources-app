"""Migrate pdap response and internal notes columns

Revision ID: 7bcc381f0344
Revises: 018aeb44ca51
Create Date: 2025-03-13 11:32:19.339802

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7bcc381f0344"
down_revision: Union[str, None] = "018aeb44ca51"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    id_and_archive_reason = [
        [109, "canada"],
        [32, "Duplicate of 1/21/23 request"],
        [28, "Canada; no contact info"],
        [22, "broad in scope, no contact with requestor"],
        [29, "Canada; no contact info"],
        [84, "not enough info"],
        [12, "open-ended"],
        [13, "open-ended"],
        [17, "impossibly broad; asked submitter for more info"],
        [82, "no"],
        [36, "No information in request"],
        [72, "indirectly about jail"],
        [85, "relevance"],
        [94, "No data"],
        [43, "open-ended"],
        [25, "records do not exist"],
        [97, "duplicate"],
        [9, "stale"],
        [33, "no response from requestor"],
        [21, "Rejected due to ethical concerns."],
    ]

    for id, archive_reason in id_and_archive_reason:
        # Replace single quotes with double quotes
        archive_reason = archive_reason.replace("'", '"')
        op.execute(
            """
            UPDATE DATA_REQUESTS
            SET archive_reason = '{}'
            WHERE id = {};
            """.format(
                archive_reason, id
            )
        )

    id_and_internal_notes = [
        ["42", "Connected with collaborators."],
        [
            "60",
            "$12767.77 in January 2023, from the ALC cash bail report. Court dockets needed for further analysis\n",
        ],
        [
            "61",
            "Holding status dashboard tells us how many are awaiting trial, but not if there was bail set.",
        ],
        ["62", "Court dockets needed for further analysis"],
        ["63", "Court docket analysis required."],
        ["68", "Court docket analysis required."],
        [
            "65",
            "Court docket analysis required, unclear from holding status / population dashboard",
        ],
        [
            "102",
            "We're working on a web scraper to answer this question: https://github.com/Police-Data-Accessibility-Project/scrapers/issues/240",
        ],
        ["91", "We're consolidating data and analysis here."],
        [
            "30",
            "https://openjustice.doj.ca.gov/data\n\nThe use of force incidents here might help people.",
        ],
        [
            "112",
            "RTK request made with the ACJ 5/8/24. #W018120-050824\xa0\n\nResponse: https://www.documentcloud.org/documents/24748029-copy_of_iron_city_complaint_form_01-03-23__002_xlsx",
        ],
        ["6", "Shared data source."],
        [
            "116",
            "A PDAP contributor responded in the GitHub issue with selected sources from our database that include demographic information. ",
        ],
        [
            "104",
            "'- The ACJ’s only policy about LGBTQ issues covers transgender and intersex people.\xa0(source) (segregated housing reports for solitary confinement context)\n- The policies from the\xa0LA sheriff’s department\xa0start on page 1745 and seem relatively recent\n- We weren’t able to find policies specific to DeKalb’s jail, but they did pass a\xa0non-discrimination ordinance\xa0with language for sexual orientation and gender identity.\n",
        ],
        ["53", "There don't seem to be records "],
        [
            "113",
            "RTK request made with the ACJ 5/8/24. #W018121-050824\n\ntheir response was to share the mortality review here: https://www.alleghenycounty.us/files/assets/county/v/1/government/jail/reports/ncchc_mortality-review-technical-assistance-report_revised.pdf\n\nAnother request made 6/13/24 for 2010–23.",
        ],
        [
            "115",
            "Start here for case access: https://www.occourts.org/online-services/case-access",
        ],
        [
            "111",
            "https://ujsportal.pacourts.us/Report/MdjDocketSheet?docketNumber=MJ-05003-CR-0002421-2024&dnh=k39BezDFiZUz7v3DfAElJA%3D%3D",
        ],
        [
            "98",
            "The City of Pittsburgh Bureau of Police (PBP) and the Allegheny County Department of Human Services (DHS) create dashboards such as this one that reports data on shots fired from 2012 onward in the city of Pittsburgh. It collects the data from 911 dispatches and can be broken down by year/month and by neighborhood. However, since there is no data county-wide (only within the City of Pittsburgh), and since 911 dispatches for the entire county are not public data, we are not able to replicate this project for the entire county.\n\nIt's worth noting this recent article from Wired about some leaked locations of ShotSpotter, which includes many in the Pittsburgh area. ShotSpotter leads to many false alarms, so it may not be a good source of firearm discharges.",
        ],
        [
            "105",
            "Answered in detail by the Allegheny County Bail Dashboard: https://public.tableau.com/app/profile/abolitionist.law.center/viz/ALCBailDashboard/ALCBailDashboard",
        ],
        [
            "101",
            "1. Current status\n    a. According to the PCPA, the Pittsburgh Bureau of Police was accredited on 1/10/2013 by the Pennsylvania Law Enforcement Accreditation Commission (PLEAC) which was developed by the Pennsylvania Chiefs of Police in 2001\n    b. Not accredited by the CALEA (Commission on Accreditation for Law Enforcement Agencies), which is a different organization (see here for more information), according to their 2022 annual report\xa0\n2. Re-accreditation procedure\n    a. According to the PCPA website, “accreditation status will remain valid for a three-year period with annual reports required”\n        i. “there is a $1,000 annual program maintenance fee for agencies whose Chief is an Active Member of PCPA. \xa0 For all others, the annual program maintenance fee is $1,250.\xa0 This annual fee does not apply until you become an accredited agency.\xa0 This fee is necessary to help defray the direct costs of your subsequent re-accreditation on-site assessments” (from FAQ page)\n3. Other info:\n    a. Civilians are allowed to be Accreditation Managers (from FAQ page)\n    b. Link to Standards Manual\n    c. In July 2022, WESA published an article summarizing how pittsburgh police was threatened by PLEAC that their accreditation would be revoked. The reason was that the city of pittsburgh passed an ordinance that prohibited police from pulling over motorists for minor infractions like a broken brake light, but PLEAC claimed this violated PA’s vehicle code. Essentially, PLEAC said the city of pittsburgh couldn’t override PA’s vehicle code, and this ordinance did that, so PLEAC threatened revocation of the accreditation (for violating their policy of following all state and federal law, including state vehicle codes).\n        i. The ordinance was originally passed as a response to disproportionate enforcement against POC, due to racial bias by police.\n        ii. Another article published by WESA in January 2023 said that the accrediation agency ultimately decided against revoking accreditation (It says: “According to Jim Adams, accreditation coordinator for the chiefs association, Pittsburgh was granted a waiver through 2025. He said that while following the ordinance runs afoul of the accreditation standards, “it was no fault of the police department or the police chief.”). However, the pittsburgh police department decided to no longer abide by the ordinance, citing officers’ inability to properly do their jobs.\n",
        ],
        [
            "31",
            'https://data-sources.pdap.io/search/roster/tennessee\nSeveral requests have been made via MuckRock.\nAgencies:\xa0https://airtable.com/shrHUW0cjWXYO4UKt\nData Sources:\xa0https://airtable.com/shr5U8UY4Loo1P1cn\nMaking FOIA requests for "A roster of current law enforcement officers at this agency, with full names and hire dates. Please provide these records in their current format."\nRelevant TN law:\nhttps://law.justia.com/codes/tennessee/2020/title-10/chapter-7/part-5/section-10-7-504/#:~:text=personnel%20information\nFOIA requests:\xa0https://www.muckrock.com/foi/mylist/?q=&status=&jurisdiction=155-True&has_embargo=&has_crowdfund=&minimum_pages=&date_range_min=&date_range_max=&file_types=&search_title=\n',
        ],
        ["24", "Made records requests with Detroit. Historic alerts; policies\n"],
        ["19", "Lodi sources shared, including crime and police statistics."],
        [
            "34",
            "Responded with Personnel Records and other recommendations; waiting to see if that was helpful/more detailed request https://airtable.com/shro9q59hsq7qbKe5",
        ],
        ["59", "Recommended a survey of incarcerated people."],
        ["39", "Connected with a volunteer."],
        ["89", "Generally, no."],
        ["1", "Source shared.\n"],
        ["2", "Source shared.\n"],
        ["57", "Recommended a survey of incarcerated people."],
        [
            "75",
            "HIPAA may make this difficult. They may not have existing records that don't mention names, they may need to create records. Recommended a survey",
        ],
        [
            "74",
            "HIPAA may make this difficult. They may not have existing records that don't mention names, they may need to create records. Recommended a survey",
        ],
        [
            "73",
            "HIPAA may make this difficult. They may not have existing records that don't mention names, they may need to create records. Recommended a survey",
        ],
        ["71", "Health inspection records are available.\n"],
        [
            "69",
            "Jail Bookings, Releases, and Length of Stay\nIn the past 3 years, median is 37 days and average is 111 days.\nCourt docket analysis would give us sentencing details.",
        ],
        [
            "67",
            "Population overview. It's not possible to learn who these youth are without court docket analysis.",
        ],
        ["66", "Segregated Housing reports tell the story, but require analysis"],
        [
            "64",
            "Holding status breakdown, Holding status trend\n42% as of 5/15/23, but pretty stable",
        ],
        [
            "58",
            '2021 survey \n"In an open-ended response, the following items were the most frequently listed as necessary items that respondents purchased at the commissary: soap, toothpaste, shampoo, deodorant, lotion, toothbrush, toilet paper, socks, food, shoes, boxers"',
        ],
        [
            "55",
            "Holding status breakdown, Holding status trend\n\nAs of 5/15/23, but these numbers are pretty stable:\n40% awaiting trial\n38% county probation detainer\n8% external detainer\n7% county sentenced\n4% PA probation detainer\n2% release condition\n1% family court\n<1% pending release",
        ],
        [
            "54",
            "Bookings & releases \nIn the last 3 years, 58 days is the average and 14 days is the median.",
        ],
        ["49", "Provided initial data sources, can do more research upon request."],
        [
            "50",
            "Response 7/7:\n\nHere’s some general information and advice about FOIA, which you may have seen: https://docs.pdap.io/activities/data-sources/foia\n\n- Most important is trying to talk to their records person—if you tell them you’re going to make a request, and that you want to make the request easy for them to grant, they will almost always help you understand what to include in the request.\n\n- Requesting complete records of complaints dating back x number of years might be more helpful, because it may actually result in less work for the records department. \n\n- You would need the complaints to include officer’s names and badge numbers; if they won’t do that for you, they probably won’t give you the complaints for specific officers.\n\n- Ideally the complaints include some kind of ID. There’s likely a table of complaints with basic details, and a corresponding more detailed file of each one. You could request the files by number.\n\n- You can specify that the records be shared in the format in which they are currently stored. Less room for error, less work, less receiving databases in PDF format.",
        ],
        ["38", "Pointed to crime and census data"],
        [
            "46",
            "connected with Atlas of Surveillance: https://atlasofsurveillance.org/search?utf8=%E2%9C%93&location=pittsburgh&commit=Search+the+Data",
        ],
        [
            "45",
            "Details for requesting the autopsy report were shared with the requestor.",
        ],
        [
            "41",
            "Answered questions about accessing the documents; did not find a way around a paid records request from the coroner",
        ],
        [
            "44",
            "connected with a collaborator and shared crash data: https://data.wprdc.org/dataset/allegheny-county-crash-data",
        ],
        [
            "40",
            "It depends how you define “clearance”—and your ability to follow a case through to prosecution. Some agencies may define their clearance rate as as arrest, but not update their numbers if the charge is dropped. \nYou could request a document about “clearance rates” from the police, but they may not have such a document lying around. You would also need to know how it was generated, and ideally see the underlying data.\n\nIn general it’s crime reports → arrests/charges → court cases/prosecutions.\n\nFBI's NIBRS database may be a good starting point. It's missing a lot of data, and it's normalized so you're missing some context, but you can compare crime to arrests in the same department across specified time periods.",
        ],
        [
            "37",
            "We successfully requested traffic stops:\xa0https://www.muckrock.com/foi/pittsburgh-130/traffic-stops-140596/\nAt least one article used the data:\xa0https://www.publicsource.org/pittsburgh-police-traffic-stop-disparity-accountability-race/",
        ],
        ["23", "Connected with a volunteer for data analysis"],
        [
            "35",
            "Record type = Incident Reports: https://airtable.com/shrJdF5DL8sqctJbh",
        ],
        [
            "27",
            "Found 3 unrelated cases searching for Christopher Allen Shipley (the alleged shooter) https://portal-nc.tylertech.cloud/Portal/\n\nAsked requestor for more info.\n\nGranted by finding the docket numbers via inmate search, and calling the courthouse who confirmed the case could be accessed only in person.",
        ],
        ["10", "Shared data source."],
        ["4", "Shared data source."],
        ["5", "Shared data source."],
        ["7", "Shared data source."],
        ["8", "Shared data source."],
        [
            "3",
            "We wrote a scraper and automated it: https://github.com/Police-Data-Accessibility-Project/github-actions-demo/",
        ],
        ["56", "Analysis of court dockets would be required to answer this question."],
    ]

    for id, internal_notes in id_and_internal_notes:
        # Replace single quotes with double quotes
        internal_notes = internal_notes.replace("'", '"')
        op.execute(
            sa.text(
                """
            UPDATE data_requests 
            SET internal_notes = :internal_notes 
            WHERE id = :id;
        """
            ).bindparams(internal_notes=internal_notes, id=int(id))
        )


def downgrade() -> None:
    pass
