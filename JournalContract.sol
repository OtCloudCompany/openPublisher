// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract JournalContract {

    struct Manuscript {
        string metadata;
        address submittedBy;
        uint256 dateSubmitted;
    }

    Manuscript[] public manuscripts;

    function publishManuscript(string memory manuscriptJson) public {
        manuscripts.push(Manuscript({
            metadata: manuscriptJson,
            submittedBy: msg.sender,
            dateSubmitted: block.timestamp
        }));
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
}
