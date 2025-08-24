// SPDX-License-Identifier: MIT

pragma solidity ^0.8.10;

contract JournalContract {

    struct Manuscript {
        string metadata;
        address submittedBy;
        uint256 dateSubmitted;
    }

    struct ReviewerAssignment {
        string manuscriptId;
        string reviewerId;
        string metadata;
    }

    struct ReviewSubmission {
        string manuscriptId;
        string reviewerId;
        string metadata;
    }

    struct AuthorCorrection {
        string manuscriptId;
        string authorId;
        string metadata;
        uint256 dateSubmitted;
    }

    Manuscript[] public manuscripts;
    ReviewerAssignment[] public reviewerAssignments;
    ReviewSubmission[] public reviewSubmissions;
    AuthorCorrection[] public authorCorrections;

    event ReviewerAssigned(string manuscriptId, string reviewerId, string metadata);
    event ReviewSubmitted(string manuscriptId, string reviewerId, string metadata);
    event CorrectionSubmitted(string manuscriptId, string authorId, string metadata);

    function publishManuscript(string memory manuscriptJson) public {
        manuscripts.push(Manuscript({
            metadata: manuscriptJson,
            submittedBy: msg.sender,
            dateSubmitted: block.timestamp
        }));
    }

    function recordReviewerAssignment(string memory manuscriptId, string memory reviewerId, string memory metadata) public {
        reviewerAssignments.push(ReviewerAssignment(manuscriptId, reviewerId, metadata));
        emit ReviewerAssigned(manuscriptId, reviewerId, metadata);
    }

    function recordReviewSubmission(string memory manuscriptId, string memory reviewerId, string memory metadata) public {
        reviewSubmissions.push(ReviewSubmission(manuscriptId, reviewerId, metadata));
        emit ReviewSubmitted(manuscriptId, reviewerId, metadata);
    }

    function recordCorrections(string memory manuscriptId, string memory authorId, string memory metadata) public {
        authorCorrections.push(AuthorCorrection({
            manuscriptId: manuscriptId,
            authorId: authorId,
            metadata: metadata,
            dateSubmitted: block.timestamp
        }));
        emit CorrectionSubmitted(manuscriptId, authorId, metadata);
    }

    function getManuscriptsCount() public view returns (uint256) {
        return manuscripts.length;
    }

    function getManuscriptDetails(uint256 index) public view returns (string memory, address, uint256) {
        require(index < manuscripts.length, "Index out of bounds");
        return (
            manuscripts[index].metadata,
            manuscripts[index].submittedBy,
            manuscripts[index].dateSubmitted
        );
    }

    function getManuscriptsBySubmitter(address submitter) public view returns (string[] memory) {
        uint256 count = 0;

        // Count the manuscripts submitted by the provided address
        for (uint256 i = 0; i < manuscripts.length; i++) {
            if (manuscripts[i].submittedBy == submitter) {
                count++;
            }
        }

        // Create an array to hold the manuscripts
        string[] memory result = new string[](count);
        uint256 index = 0;

        // Retrieve the manuscripts submitted by the provided address
        for (uint256 i = 0; i < manuscripts.length; i++) {
            if (manuscripts[i].submittedBy == submitter) {
                result[index] = manuscripts[i].metadata;
                index++;
            }
        }
        return result;
    }

    function getManuscriptById(uint256 manuscriptId) public view returns (Manuscript memory) {
        require(manuscriptId < manuscripts.length, "Manuscript does not exist");
        return manuscripts[manuscriptId];
    }
}