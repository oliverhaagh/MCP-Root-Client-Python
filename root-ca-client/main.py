#  Copyright 2020 Maritime Connectivity Platform Consortium
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import requests
import argparse


def main():
    parser = argparse.ArgumentParser(description='Utility for interacting with the MCP root CA service')
    parser.add_argument('-c', '--create', nargs=1, metavar='PEM cert',
                        help='Create a new Root CA. Takes the path of a PEM '
                             'certificate as argument')
    parser.add_argument('-gr', '--get-root', dest='gr', nargs=1, metavar='root ID',
                        help='Gets the root CA that has the specified ID')
    parser.add_argument('-gar', '--get-all-roots', dest='gar', action='store_true',
                        help='Gets either all root CAs, or if a list of attestor IDs is given the list of root CAs that'
                             ' are attested by the given attestors will be returned')
    parser.add_argument('-atby', '--get-attested-by', dest='atby', nargs='+', metavar='attestor IDs',
                        help='Get all root CAs that are attested by the given attestors')
    parser.add_argument('-ca', '--create-attestor', dest='ca', nargs=1, metavar='PEM cert',
                        help='Create a new attestor. Takes the path of a PEM certificate as argument')
    parser.add_argument('-ga', '--get-attestor', dest='ga', nargs=1, metavar='attestor ID',
                        help='Gets the attestor that has the specified ID')
    parser.add_argument('-gaa', '--get-all-attestors', dest='gaa', action='store_true',
                        help='Gets the list of all attestors')
    parser.add_argument('-catt', '--create-attestation', dest='catt', nargs=4,
                        metavar=('attestor-ID', 'root-CA-ID', 'signature-file', 'signature-algorithm-identifier'),
                        help='Create a new attestation')
    parser.add_argument('-gat', '--get-attestation', dest='gat', nargs=1, metavar='attestation ID',
                        help='Gets the attestation with '
                             'the specified ID')
    parser.add_argument('-gaat', '--get-all-attestations', dest='gaat', action='store_true',
                        help='Get the list of all attestations')
    parser.add_argument('-cre', '--create-revocation', nargs=5, metavar=(
    'attestor-ID', 'root-CA-ID', 'attestation-id', 'signature-file', 'signature-algorithm-identifier'),
                        help='Revokes an attestation')
    parser.add_argument('-gre', '--get-revocation', nargs=1, metavar='revocation ID',
                        help='Get the revocation with the specified ID')
    parser.add_argument('-gres', '--get-all-revocations', dest='gres', action='store_true', help='Gets all revocations')
    parser.add_argument('-o', '--outfile', nargs=1, metavar='output file',
                        help='Writes the output to the specified path')
    args = parser.parse_args()
    url = 'http://localhost:8080/api'

    if args.create:
        pem_cert_path = args.create[0]
        with open(pem_cert_path, "rb") as h:
            pem_cert = h.read()
        r = requests.post(url + '/root', data=pem_cert, headers={'Content-Type': 'application/x-pem-file'})
        write_response(args, r)
    elif args.gr:
        root_id = args.gr[0]
        r = requests.get(url + '/root/' + root_id)
        write_response(args, r)
    elif args.gar:
        r = requests.get(url + '/roots')
        write_certs(args, r)
    elif args.atby:
        tmp = ['attestorId={}'.format(att_id) for att_id in args.atby]
        variables = '?' + '&'.join(tmp)
        tmp_url = f"{url}/roots{variables}"
        r = requests.get(tmp_url)
        write_certs(args, r)
    elif args.ca:
        pem_cert_path = args.ca[0]
        with open(pem_cert_path, "wb") as h:
            pem_cert = h.read()
        r = requests.post(url + '/attestor', data=pem_cert,
                          headers={'Content-Type': 'application/pem-certificate-chain'})
        write_response(args, r)
    elif args.ga:
        att_id = args.ga[0]
        r = requests.get(url + '/attestor/' + att_id)
        write_response(args, r)
    elif args.gaa:
        r = requests.get(url + '/attestors')
        write_response(args, r)
    elif args.catt:
        att_id = args.catt[0]
        root_id = args.catt[1]
        sig_path = args.catt[2]
        sig_alg = args.catt[3]
        with open(sig_path, "rb") as h:
            sig = h.read()
        sig_hex = sig.hex()
        data = {'attestorId': att_id, 'rootCAid': root_id, 'signature': sig_hex, 'algorithmIdentifier': sig_alg}
        r = requests.post(url + '/attestation', json=data)
        write_response(args, r)
    elif args.gat:
        attest_id = args.gat[0]
        r = requests.get(url + '/attestation/' + attest_id)
        write_response(args, r)
    elif args.gaat:
        r = requests.get(url + '/attestations')
        write_response(args, r)
    elif args.cre:
        att_id = args.catt[0]
        root_id = args.catt[1]
        attest_id = args.catt[2]
        sig_path = args.catt[3]
        sig_alg = args.catt[4]
        with open(sig_path, "rb") as h:
            sig = h.read()
        sig_hex = sig.hex()
        data = {'attestorId': att_id, 'rootCAid': root_id, 'attestationId': attest_id, 'signature': sig_hex,
                'algorithmIdentifier': sig_alg}
        r = requests.post(url + '/revocation', json=data)
        write_response(args, r)
    elif args.gre:
        rev_id = args.gre[0]
        r = requests.get(url + '/revocation/' + rev_id)
        write_response(args, r)
    elif args.gres:
        r = requests.get(url + '/revocations')
        write_response(args, r)


def write_response(args, r):
    if r.status_code == 200:
        cont = r.json()
        if args.outfile:
            with open(args.outfile, "w") as h:
                h.write(cont)
        print(cont)
    else:
        print(r.text)


def write_certs(args, r):
    if r.status_code == 200:
        cont = r.json()
        if args.outfile:
            certs = [root['certificate'] for root in cont]
            certs_str = ''.join(certs)
            with open(args.outfile[0], "wb") as h:
                h.write(bytes(certs_str, encoding="UTF-8"))
        print(cont)
    else:
        print(r.text)


if __name__ == '__main__':
    main()
